from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
import stripe
import os
from datetime import datetime, timedelta

payment_bp = Blueprint('payment', __name__)

# Configuration Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@payment_bp.route('/payment/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Créer une session de paiement Stripe"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Ne pas permettre aux superadmins de payer
        if user.is_superadmin:
            return jsonify({'error': 'Les superadmins n\'ont pas besoin d\'abonnement'}), 400
        
        # Vérifier si l'utilisateur a déjà un abonnement actif
        if user.subscription_status == 'active':
            return jsonify({'error': 'Vous avez déjà un abonnement actif'}), 400
        
        # Créer ou récupérer le client Stripe
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                metadata={'user_id': str(user.id)}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
        
        # URL de base pour les redirections
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        
        # Créer la session de paiement
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Abonnement SmartLinks - 1 an',
                        'description': 'Accès complet à SmartLinks pour 12 mois',
                    },
                    'unit_amount': 50000,  # 500€ en centimes
                    'recurring': {
                        'interval': 'year',
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{frontend_url}/payment/cancel',
            metadata={
                'user_id': str(user.id)
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Erreur Stripe: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la création de la session: {str(e)}'}), 500

@payment_bp.route('/payment/verify-session/<session_id>', methods=['GET'])
@jwt_required()
def verify_payment_session(session_id):
    """Vérifier le statut d'une session de paiement"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Récupérer la session Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Vérifier que la session appartient à l'utilisateur
        if session.metadata.get('user_id') != str(user.id):
            return jsonify({'error': 'Session non autorisée'}), 403
        
        if session.payment_status == 'paid':
            # Récupérer les détails de l'abonnement
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            # Mettre à jour l'utilisateur
            user.subscription_status = 'active'
            user.stripe_subscription_id = subscription.id
            user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Paiement confirmé et abonnement activé',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'status': 'pending',
                'message': 'Paiement en cours de traitement'
            }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Erreur Stripe: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la vérification: {str(e)}'}), 500

@payment_bp.route('/payment/webhook', methods=['POST'])
def stripe_webhook():
    """Webhook Stripe pour les événements de paiement"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        if not endpoint_secret:
            return jsonify({'error': 'Webhook secret non configuré'}), 400
        
        # Vérifier la signature du webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        
        # Traiter les événements
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata'].get('user_id')
            
            if user_id:
                user = User.query.get(int(user_id))
                if user:
                    # Récupérer les détails de l'abonnement
                    subscription = stripe.Subscription.retrieve(session['subscription'])
                    
                    user.subscription_status = 'active'
                    user.stripe_subscription_id = subscription.id
                    user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
                    
                    db.session.commit()
        
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            subscription_id = invoice['subscription']
            
            if subscription_id:
                user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
                if user:
                    # Renouveler l'abonnement
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    user.subscription_status = 'active'
                    user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
                    
                    db.session.commit()
        
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            subscription_id = invoice['subscription']
            
            if subscription_id:
                user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
                if user:
                    user.subscription_status = 'expired'
                    db.session.commit()
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            subscription_id = subscription['id']
            
            user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
            if user:
                user.subscription_status = 'cancelled'
                user.stripe_subscription_id = None
                db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Signature webhook invalide'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur webhook: {str(e)}'}), 500

@payment_bp.route('/payment/subscription-status', methods=['GET'])
@jwt_required()
def get_subscription_status():
    """Obtenir le statut d'abonnement de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Si c'est un superadmin, retourner un statut spécial
        if user.is_superadmin:
            return jsonify({
                'subscription_status': 'unlimited',
                'is_superadmin': True,
                'message': 'Accès illimité - Superadmin'
            }), 200
        
        response_data = {
            'subscription_status': user.subscription_status,
            'subscription_end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
            'is_superadmin': False
        }
        
        # Si l'abonnement est actif, vérifier s'il n'est pas expiré
        if user.subscription_status == 'active' and user.subscription_end_date:
            if datetime.utcnow() > user.subscription_end_date:
                user.subscription_status = 'expired'
                db.session.commit()
                response_data['subscription_status'] = 'expired'
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération du statut: {str(e)}'}), 500

@payment_bp.route('/payment/cancel-subscription', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Annuler l'abonnement de l'utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        if not user.stripe_subscription_id:
            return jsonify({'error': 'Aucun abonnement actif trouvé'}), 400
        
        # Annuler l'abonnement dans Stripe
        stripe.Subscription.delete(user.stripe_subscription_id)
        
        # Mettre à jour l'utilisateur
        user.subscription_status = 'cancelled'
        user.stripe_subscription_id = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Abonnement annulé avec succès',
            'user': user.to_dict()
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Erreur Stripe: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Erreur lors de l\'annulation: {str(e)}'}), 500

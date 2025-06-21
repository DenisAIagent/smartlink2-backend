from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User, Smartlink, Platform
from functools import wraps
import os

admin_bp = Blueprint('admin', __name__)

def superadmin_required(f):
    """Décorateur pour vérifier les droits de superadmin"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_superadmin:
            return jsonify({'error': 'Accès refusé - Droits de superadmin requis'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin/users', methods=['GET'])
@superadmin_required
def get_all_users():
    """Récupérer tous les utilisateurs - Superadmin seulement"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        
        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search))
            )
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict(include_admin_fields=True) for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des utilisateurs: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@superadmin_required
def update_user_admin(user_id):
    """Mettre à jour un utilisateur - Superadmin seulement"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Mise à jour des champs autorisés
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'subscription_status' in data:
            valid_statuses = ['pending', 'active', 'expired', 'cancelled']
            if data['subscription_status'] in valid_statuses:
                user.subscription_status = data['subscription_status']
            else:
                return jsonify({'error': 'Statut d\'abonnement invalide'}), 400
        
        if 'is_superadmin' in data:
            user.is_superadmin = bool(data['is_superadmin'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'user': user.to_dict(include_admin_fields=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@superadmin_required
def delete_user_admin(user_id):
    """Supprimer un utilisateur - Superadmin seulement"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Ne pas permettre de se supprimer soi-même
        current_user_id = get_jwt_identity()
        if user_id == current_user_id:
            return jsonify({'error': 'Impossible de supprimer votre propre compte'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@admin_bp.route('/admin/smartlinks', methods=['GET'])
@superadmin_required
def get_all_smartlinks():
    """Récupérer tous les smartlinks - Superadmin seulement"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Smartlink.query
        
        if user_id:
            query = query.filter(Smartlink.user_id == user_id)
        
        smartlinks = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'smartlinks': [smartlink.to_dict() for smartlink in smartlinks.items],
            'total': smartlinks.total,
            'pages': smartlinks.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des smartlinks: {str(e)}'}), 500

@admin_bp.route('/admin/smartlinks/<string:smartlink_id>', methods=['DELETE'])
@superadmin_required
def delete_smartlink_admin(smartlink_id):
    """Supprimer un smartlink - Superadmin seulement"""
    try:
        smartlink = Smartlink.query.get_or_404(smartlink_id)
        
        db.session.delete(smartlink)
        db.session.commit()
        
        return jsonify({'message': 'Smartlink supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la suppression: {str(e)}'}), 500

@admin_bp.route('/admin/stats', methods=['GET'])
@superadmin_required
def get_admin_stats():
    """Récupérer les statistiques globales - Superadmin seulement"""
    try:
        # Compter les utilisateurs par statut
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Compter les abonnements par statut
        pending_subscriptions = User.query.filter_by(subscription_status='pending').count()
        active_subscriptions = User.query.filter_by(subscription_status='active').count()
        expired_subscriptions = User.query.filter_by(subscription_status='expired').count()
        cancelled_subscriptions = User.query.filter_by(subscription_status='cancelled').count()
        
        # Compter les smartlinks
        total_smartlinks = Smartlink.query.count()
        total_views = db.session.query(db.func.sum(Smartlink.views)).scalar() or 0
        total_clicks = db.session.query(db.func.sum(Smartlink.clicks)).scalar() or 0
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'inactive': total_users - active_users
            },
            'subscriptions': {
                'pending': pending_subscriptions,
                'active': active_subscriptions,
                'expired': expired_subscriptions,
                'cancelled': cancelled_subscriptions
            },
            'smartlinks': {
                'total': total_smartlinks,
                'total_views': total_views,
                'total_clicks': total_clicks
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération des statistiques: {str(e)}'}), 500

@admin_bp.route('/admin/create-superadmin', methods=['POST'])
def create_initial_superadmin():
    """Créer le premier superadmin - Disponible seulement s'il n'y en a pas"""
    try:
        # Vérifier s'il existe déjà un superadmin
        existing_superadmin = User.query.filter_by(is_superadmin=True).first()
        if existing_superadmin:
            return jsonify({'error': 'Un superadmin existe déjà'}), 409
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Nom d\'utilisateur, email et mot de passe requis'}), 400
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 409
        
        # Créer le superadmin
        superadmin = User(
            username=username,
            email=email,
            is_superadmin=True,
            subscription_status='active'  # Les superadmins ont un accès illimité
        )
        superadmin.set_password(password)
        
        db.session.add(superadmin)
        db.session.commit()
        
        return jsonify({
            'message': 'Superadmin créé avec succès',
            'user': superadmin.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création du superadmin: {str(e)}'}), 500

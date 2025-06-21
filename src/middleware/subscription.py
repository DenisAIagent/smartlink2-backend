from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from src.models.user import User
from datetime import datetime

def subscription_required(f):
    """Décorateur pour vérifier qu'un utilisateur a un abonnement actif"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Les superadmins ont toujours accès
        if user.is_superadmin:
            return f(*args, **kwargs)
        
        # Vérifier le statut d'abonnement
        if user.subscription_status != 'active':
            return jsonify({
                'error': 'Abonnement requis',
                'message': 'Cette fonctionnalité nécessite un abonnement actif',
                'subscription_status': user.subscription_status,
                'requires_payment': True
            }), 402  # Payment Required
        
        # Vérifier si l'abonnement n'est pas expiré
        if user.subscription_end_date and datetime.utcnow() > user.subscription_end_date:
            # Mettre à jour le statut en base
            user.subscription_status = 'expired'
            from src.models.user import db
            db.session.commit()
            
            return jsonify({
                'error': 'Abonnement expiré',
                'message': 'Votre abonnement a expiré, veuillez le renouveler',
                'subscription_status': 'expired',
                'requires_payment': True
            }), 402  # Payment Required
        
        return f(*args, **kwargs)
    
    return decorated_function

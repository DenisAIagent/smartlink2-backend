from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Smartlink, Platform, User
from src.middleware.subscription import subscription_required
from datetime import datetime
import string
import random

smartlink_bp = Blueprint('smartlink', __name__)

def generate_smartlink_id():
    """Génère un ID unique pour un smartlink"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

@smartlink_bp.route('/smartlinks', methods=['POST'])
@jwt_required()
@subscription_required
def create_smartlink():
    """Créer un nouveau smartlink"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Validation des champs requis
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Le titre est requis'}), 400
        
        # Générer un ID unique
        smartlink_id = generate_smartlink_id()
        while Smartlink.query.get(smartlink_id):
            smartlink_id = generate_smartlink_id()
        
        # Créer le nouveau smartlink
        smartlink = Smartlink(
            id=smartlink_id,
            title=title,
            description=data.get('description'),
            url=data.get('url'),
            views=0,
            clicks=0,
            landing_page_title=data.get('landing_page_title'),
            landing_page_subtitle=data.get('landing_page_subtitle'),
            cover_image_url=data.get('cover_image_url'),
            embed_url=data.get('embed_url'),
            long_description=data.get('long_description'),
            social_sharing_enabled=data.get('social_sharing_enabled', True),
            user_id=current_user_id
        )
        
        db.session.add(smartlink)
        db.session.flush()  # Pour obtenir l'ID avant de créer les plateformes
        
        # Gérer les plateformes avec le nouveau modèle normalisé
        platforms_data = data.get('platforms', [])
        for i, platform_data in enumerate(platforms_data):
            if 'name' in platform_data and 'url' in platform_data:
                platform = Platform(
                    name=platform_data['name'],
                    url=platform_data['url'],
                    icon=platform_data.get('icon'),
                    order_index=i,
                    smartlink_id=smartlink_id
                )
                db.session.add(platform)
        
        db.session.commit()
        
        return jsonify(smartlink.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks', methods=['GET'])
@jwt_required()
def get_user_smartlinks():
    """Récupérer tous les smartlinks de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        smartlinks = Smartlink.query.filter_by(user_id=current_user_id).order_by(Smartlink.created_at.desc()).all()
        return jsonify([smartlink.to_dict() for smartlink in smartlinks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>', methods=['GET'])
@jwt_required()
def get_smartlink_owner(smartlink_id):
    """Récupérer un smartlink spécifique pour le propriétaire"""
    try:
        current_user_id = get_jwt_identity()
        smartlink = Smartlink.query.filter_by(id=smartlink_id, user_id=current_user_id).first()
        
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé ou accès non autorisé'}), 404
        
        return jsonify(smartlink.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/public/smartlinks/<string:smartlink_id>', methods=['GET'])
def get_smartlink_public(smartlink_id):
    """Récupérer un smartlink spécifique pour vue publique (sans authentification)"""
    try:
        smartlink = Smartlink.query.get(smartlink_id)
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé'}), 404
        
        # Incrémenter le nombre de vues
        smartlink.views += 1
        db.session.commit()
        
        return jsonify(smartlink.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>', methods=['PUT'])
@jwt_required()
@subscription_required
def update_smartlink(smartlink_id):
    """Mettre à jour un smartlink"""
    try:
        current_user_id = get_jwt_identity()
        smartlink = Smartlink.query.filter_by(id=smartlink_id, user_id=current_user_id).first()
        
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé ou accès non autorisé'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Mettre à jour les champs de base
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': 'Le titre ne peut pas être vide'}), 400
            smartlink.title = title
        if 'description' in data:
            smartlink.description = data['description']
        if 'url' in data:
            smartlink.url = data['url']
        
        # Mettre à jour les champs de la page de destination
        if 'landing_page_title' in data:
            smartlink.landing_page_title = data['landing_page_title']
        if 'landing_page_subtitle' in data:
            smartlink.landing_page_subtitle = data['landing_page_subtitle']
        if 'cover_image_url' in data:
            smartlink.cover_image_url = data['cover_image_url']
        if 'embed_url' in data:
            smartlink.embed_url = data['embed_url']
        if 'long_description' in data:
            smartlink.long_description = data['long_description']
        if 'social_sharing_enabled' in data:
            smartlink.social_sharing_enabled = data['social_sharing_enabled']
        
        # Mettre à jour les plateformes avec le nouveau modèle normalisé
        if 'platforms' in data:
            # Supprimer les anciennes plateformes
            Platform.query.filter_by(smartlink_id=smartlink_id).delete()
            
            # Ajouter les nouvelles plateformes
            platforms_data = data['platforms']
            for i, platform_data in enumerate(platforms_data):
                if 'name' in platform_data and 'url' in platform_data:
                    platform = Platform(
                        name=platform_data['name'],
                        url=platform_data['url'],
                        icon=platform_data.get('icon'),
                        order_index=i,
                        clicks=platform_data.get('clicks', 0),
                        smartlink_id=smartlink_id
                    )
                    db.session.add(platform)
        
        smartlink.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(smartlink.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>', methods=['DELETE'])
@jwt_required()
@subscription_required
def delete_smartlink(smartlink_id):
    """Supprimer un smartlink"""
    try:
        current_user_id = get_jwt_identity()
        smartlink = Smartlink.query.filter_by(id=smartlink_id, user_id=current_user_id).first()
        
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé ou accès non autorisé'}), 404
        
        db.session.delete(smartlink)
        db.session.commit()
        
        return jsonify({'message': 'Smartlink supprimé avec succès'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>/click', methods=['POST'])
def track_click(smartlink_id):
    """Enregistrer un clic sur un smartlink (route publique)"""
    try:
        smartlink = Smartlink.query.get(smartlink_id)
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé'}), 404
        
        # Incrémenter le nombre de clics
        smartlink.clicks += 1
        db.session.commit()
        
        return jsonify({
            'message': 'Clic enregistré avec succès',
            'clicks': smartlink.clicks
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>/landing', methods=['GET'])
def get_smartlink_landing_page(smartlink_id):
    """Récupérer les données complètes d'une page de destination (route publique)"""
    try:
        smartlink = Smartlink.query.get(smartlink_id)
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé'}), 404
        
        # Incrémenter le nombre de vues
        smartlink.views += 1
        db.session.commit()
        
        # Retourner toutes les données nécessaires pour la page de destination
        landing_data = {
            'id': smartlink.id,
            'landing_page_title': smartlink.landing_page_title or smartlink.title,
            'landing_page_subtitle': smartlink.landing_page_subtitle,
            'cover_image_url': smartlink.cover_image_url,
            'platforms': [platform.to_dict() for platform in smartlink.platforms],
            'embed_url': smartlink.embed_url,
            'long_description': smartlink.long_description or smartlink.description,
            'social_sharing_enabled': smartlink.social_sharing_enabled,
            'views': smartlink.views,
            'clicks': smartlink.clicks
        }
        
        return jsonify(landing_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>/platforms/<int:platform_id>/click', methods=['POST'])
def track_platform_click(smartlink_id, platform_id):
    """Enregistrer un clic sur une plateforme spécifique (route publique)"""
    try:
        smartlink = Smartlink.query.get(smartlink_id)
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé'}), 404
        
        platform = Platform.query.filter_by(id=platform_id, smartlink_id=smartlink_id).first()
        if not platform:
            return jsonify({'error': 'Plateforme non trouvée'}), 404
        
        # Incrémenter les compteurs de clics
        smartlink.clicks += 1
        platform.clicks += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Clic sur la plateforme enregistré avec succès',
            'total_clicks': smartlink.clicks,
            'platform_clicks': platform.clicks,
            'redirect_url': platform.url
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@smartlink_bp.route('/smartlinks/<string:smartlink_id>/analytics', methods=['GET'])
@jwt_required()
def get_smartlink_analytics(smartlink_id):
    """Récupérer les analytics détaillées d'un smartlink"""
    try:
        current_user_id = get_jwt_identity()
        smartlink = Smartlink.query.filter_by(id=smartlink_id, user_id=current_user_id).first()
        
        if not smartlink:
            return jsonify({'error': 'Smartlink non trouvé ou accès non autorisé'}), 404
        
        # Calculer les statistiques des plateformes
        platform_stats = []
        total_platform_clicks = 0
        
        for platform in smartlink.platforms:
            total_platform_clicks += platform.clicks
            platform_stats.append({
                'id': platform.id,
                'name': platform.name,
                'clicks': platform.clicks,
                'percentage': 0  # Sera calculé après
            })
        
        # Calculer les pourcentages
        for stat in platform_stats:
            stat['percentage'] = (stat['clicks'] / total_platform_clicks * 100) if total_platform_clicks > 0 else 0
        
        analytics_data = {
            'smartlink_id': smartlink.id,
            'title': smartlink.title,
            'total_views': smartlink.views,
            'total_clicks': smartlink.clicks,
            'click_through_rate': (smartlink.clicks / smartlink.views * 100) if smartlink.views > 0 else 0,
            'created_at': smartlink.created_at.isoformat(),
            'platform_stats': platform_stats
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


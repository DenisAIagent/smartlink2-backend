from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from src.models.user import db, User
from email_validator import validate_email, EmailNotValidError
import re

auth_bp = Blueprint('auth', __name__)

def validate_password(password):
    """Valide la complexité du mot de passe"""
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    if not re.search(r"[A-Za-z]", password):
        return False, "Le mot de passe doit contenir au moins une lettre"
    if not re.search(r"\d", password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    return True, "Mot de passe valide"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation des champs requis
        if not username:
            return jsonify({'error': 'Le nom d\'utilisateur est requis'}), 400
        if not email:
            return jsonify({'error': 'L\'email est requis'}), 400
        if not password:
            return jsonify({'error': 'Le mot de passe est requis'}), 400
        
        # Validation du nom d'utilisateur
        if len(username) < 3:
            return jsonify({'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return jsonify({'error': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, traits d\'union et underscores'}), 400
        
        # Validation de l'email
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Format d\'email invalide'}), 400
        
        # Validation du mot de passe
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 409
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 409
        
        # Créer le nouvel utilisateur
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Créer les tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'inscription: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email:
            return jsonify({'error': 'Nom d\'utilisateur ou email requis'}), 400
        if not password:
            return jsonify({'error': 'Mot de passe requis'}), 400
        
        # Chercher l'utilisateur par username ou email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Identifiants invalides'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Compte désactivé'}), 401
        
        # Créer les tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Connexion réussie',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la connexion: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchit le token d'accès"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Utilisateur non trouvé ou inactif'}), 404
        
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors du rafraîchissement: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Récupère les informations de l'utilisateur connecté"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la récupération: {str(e)}'}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Met à jour le profil utilisateur"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        # Mise à jour du nom d'utilisateur
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                if User.query.filter_by(username=new_username).first():
                    return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 409
                if len(new_username) < 3:
                    return jsonify({'error': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}), 400
                if not re.match(r'^[a-zA-Z0-9_-]+$', new_username):
                    return jsonify({'error': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, traits d\'union et underscores'}), 400
                user.username = new_username
        
        # Mise à jour de l'email
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email != user.email:
                try:
                    validate_email(new_email)
                except EmailNotValidError:
                    return jsonify({'error': 'Format d\'email invalide'}), 400
                if User.query.filter_by(email=new_email).first():
                    return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 409
                user.email = new_email
        
        # Mise à jour du mot de passe
        if 'new_password' in data:
            current_password = data.get('current_password', '')
            new_password = data.get('new_password', '')
            
            if not user.check_password(current_password):
                return jsonify({'error': 'Mot de passe actuel incorrect'}), 401
            
            is_valid, message = validate_password(new_password)
            if not is_valid:
                return jsonify({'error': message}), 400
            
            user.set_password(new_password)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profil mis à jour avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la mise à jour: {str(e)}'}), 500

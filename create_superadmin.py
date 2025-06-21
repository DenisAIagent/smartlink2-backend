#!/usr/bin/env python3
"""
Script pour créer le premier superadmin SmartLinks
Usage: python create_superadmin.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User
from src.main import app
import getpass

def create_superadmin():
    """Créer le premier compte superadmin"""
    
    with app.app_context():
        # Vérifier s'il existe déjà un superadmin
        existing_superadmin = User.query.filter_by(is_superadmin=True).first()
        if existing_superadmin:
            print(f"❌ Un superadmin existe déjà: {existing_superadmin.username}")
            return False
        
        print("🔧 Création du premier superadmin SmartLinks")
        print("=" * 50)
        
        # Demander les informations
        username = input("Nom d'utilisateur: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Mot de passe: ")
        confirm_password = getpass.getpass("Confirmer le mot de passe: ")
        
        # Validation basique
        if not username or not email or not password:
            print("❌ Tous les champs sont requis")
            return False
        
        if password != confirm_password:
            print("❌ Les mots de passe ne correspondent pas")
            return False
        
        if len(password) < 8:
            print("❌ Le mot de passe doit contenir au moins 8 caractères")
            return False
        
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(username=username).first():
            print(f"❌ Le nom d'utilisateur '{username}' existe déjà")
            return False
        
        if User.query.filter_by(email=email).first():
            print(f"❌ L'email '{email}' est déjà utilisé")
            return False
        
        try:
            # Créer le superadmin
            superadmin = User(
                username=username,
                email=email,
                is_superadmin=True,
                subscription_status='active'  # Accès illimité pour les superadmins
            )
            superadmin.set_password(password)
            
            db.session.add(superadmin)
            db.session.commit()
            
            print(f"✅ Superadmin créé avec succès!")
            print(f"   Nom d'utilisateur: {username}")
            print(f"   Email: {email}")
            print(f"   ID: {superadmin.id}")
            print()
            print("🚀 Vous pouvez maintenant vous connecter avec ces identifiants.")
            print("   L'interface d'administration sera accessible à /admin")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la création: {str(e)}")
            return False

if __name__ == "__main__":
    success = create_superadmin()
    sys.exit(0 if success else 1)

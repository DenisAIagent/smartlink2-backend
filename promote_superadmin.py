#!/usr/bin/env python3
"""
Script pour promouvoir un utilisateur existant en superadmin
Usage: python promote_superadmin.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User
from src.main import app

def promote_to_superadmin():
    """Promouvoir un utilisateur existant en superadmin"""
    
    with app.app_context():
        print("🔧 Promotion d'un utilisateur en superadmin")
        print("=" * 50)
        
        # Rechercher l'utilisateur par nom d'utilisateur ou email
        identifier = input("Nom d'utilisateur ou email à promouvoir: ").strip()
        
        if not identifier:
            print("❌ Veuillez entrer un nom d'utilisateur ou email")
            return False
        
        # Chercher l'utilisateur
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user:
            print(f"❌ Aucun utilisateur trouvé avec '{identifier}'")
            
            # Lister tous les utilisateurs pour aide
            print("\n📋 Utilisateurs existants:")
            users = User.query.all()
            for u in users:
                print(f"   - {u.username} ({u.email}) - Superadmin: {u.is_superadmin}")
            return False
        
        # Vérifier s'il est déjà superadmin
        if user.is_superadmin:
            print(f"✅ {user.username} est déjà superadmin")
            return True
        
        try:
            # Promouvoir en superadmin
            user.is_superadmin = True
            user.subscription_status = 'active'  # Accès illimité
            user.is_active = True
            
            db.session.commit()
            
            print(f"✅ Utilisateur promu avec succès!")
            print(f"   Nom d'utilisateur: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Superadmin: {user.is_superadmin}")
            print(f"   Abonnement: {user.subscription_status}")
            print()
            print("🚀 L'utilisateur a maintenant accès à:")
            print("   - Toutes les fonctionnalités SmartLinks")
            print("   - Interface d'administration à /admin")
            print("   - Création illimitée de SmartLinks")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur lors de la promotion: {str(e)}")
            return False

def auto_promote_user(username_or_email):
    """Promouvoir automatiquement un utilisateur spécifique"""
    with app.app_context():
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user:
            user.is_superadmin = True
            user.subscription_status = 'active'
            user.is_active = True
            db.session.commit()
            print(f"✅ {user.username} promu en superadmin automatiquement")
            return True
        return False

if __name__ == "__main__":
    # Auto-promotion pour Denis
    if auto_promote_user("Denisadam") or auto_promote_user("denis@mdmcmusicads.com"):
        print("🎉 Denis promu en superadmin!")
        sys.exit(0)
    else:
        # Mode interactif
        success = promote_to_superadmin()
        sys.exit(0 if success else 1)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Nouveau : Système d'administration et paiement
    is_superadmin = db.Column(db.Boolean, default=False, nullable=False)
    subscription_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, active, expired, cancelled
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Relations
    smartlinks = db.relationship('Smartlink', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash et enregistre le mot de passe"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie si le mot de passe est correct"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_admin_fields=False):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'is_superadmin': self.is_superadmin,
            'subscription_status': self.subscription_status,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None
        }
        
        # Inclure les champs Stripe seulement pour les superadmins
        if include_admin_fields:
            data.update({
                'stripe_customer_id': self.stripe_customer_id,
                'stripe_subscription_id': self.stripe_subscription_id
            })
        
        return data

class Smartlink(db.Model):
    __tablename__ = 'smartlinks'
    
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    clicks = db.Column(db.Integer, default=0, nullable=False)
    
    # Champs pour la page de destination personnalisable
    landing_page_title = db.Column(db.String(255), nullable=True)
    landing_page_subtitle = db.Column(db.String(255), nullable=True)
    cover_image_url = db.Column(db.Text, nullable=True)
    embed_url = db.Column(db.Text, nullable=True)
    long_description = db.Column(db.Text, nullable=True)
    social_sharing_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Clé étrangère vers l'utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    platforms = db.relationship('Platform', backref='smartlink', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Smartlink {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'views': self.views,
            'clicks': self.clicks,
            'landing_page_title': self.landing_page_title,
            'landing_page_subtitle': self.landing_page_subtitle,
            'cover_image_url': self.cover_image_url,
            'embed_url': self.embed_url,
            'long_description': self.long_description,
            'social_sharing_enabled': self.social_sharing_enabled,
            'user_id': self.user_id,
            'platforms': [platform.to_dict() for platform in self.platforms]
        }

class Platform(db.Model):
    __tablename__ = 'platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    clicks = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Clé étrangère vers le smartlink
    smartlink_id = db.Column(db.String(50), db.ForeignKey('smartlinks.id'), nullable=False)

    def __repr__(self):
        return f'<Platform {self.name} for {self.smartlink_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'icon': self.icon,
            'order_index': self.order_index,
            'clicks': self.clicks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'smartlink_id': self.smartlink_id
        }


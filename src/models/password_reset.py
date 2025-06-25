from src.models.user import db
from datetime import datetime, timedelta
import secrets
import string

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    # Relation avec l'utilisateur
    user = db.relationship('User', backref='password_reset_tokens')
    
    def __init__(self, user_id, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.token = self._generate_token()
        self.expires_at = datetime.utcnow() + timedelta(hours=1)  # Token valide 1 heure
    
    @staticmethod
    def _generate_token():
        """Génère un token sécurisé pour la récupération de mot de passe"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @classmethod
    def create_token(cls, user_id):
        """Crée un nouveau token de récupération pour un utilisateur"""
        cls.query.filter_by(user_id=user_id, used=False).update({'used': True, 'used_at': datetime.utcnow()})
        reset_token = cls(user_id=user_id)
        db.session.add(reset_token)
        db.session.commit()
        return reset_token
    
    def is_valid(self):
        return (
            not self.used and 
            datetime.utcnow() < self.expires_at
        )
    
    def mark_as_used(self):
        self.used = True
        self.used_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'token': self.token,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'used': self.used,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:8]}... for user {self.user_id}>'

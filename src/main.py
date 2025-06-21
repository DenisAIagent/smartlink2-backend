import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv

from src.models.user import db, migrate
from src.routes.user import user_bp
from src.routes.smartlink import smartlink_bp
from src.routes.auth import auth_bp
from src.routes.proxy import proxy_bp
from src.routes.admin import admin_bp
from src.routes.payment import payment_bp

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration sécurisée
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Configuration CORS sécurisée
cors_origins_str = os.environ.get('CORS_ORIGINS', 'http://localhost:5173')
# Nettoyer les séparateurs multiples et les espaces
cors_origins = []
for origin in cors_origins_str.replace(';', ',').split(','):
    cleaned = origin.strip()
    if cleaned:
        cors_origins.append(cleaned)

print(f"CORS Origins configurées: {cors_origins}")  # Debug en production
print("🚀 SmartLinks Backend v2.0 - Promotion superadmin activée")  # Force redeploy

CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Configuration de la base de données
database_url = os.environ.get("DATABASE_URL", "sqlite:///test_smartlinks.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Debug: Afficher le type de base de données utilisée
db_type = "SQLite" if database_url.startswith("sqlite") else "MySQL/PostgreSQL"
print(f"🗄️ Base de données: {db_type}")
if not database_url.startswith("sqlite"):
    # Masquer les credentials dans les logs
    safe_url = database_url.split('@')[1] if '@' in database_url else database_url
    print(f"🔗 Connexion: {safe_url}")

# Initialisation des extensions
db.init_app(app)
migrate.init_app(app, db)
jwt = JWTManager(app)

# Enregistrement des blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(smartlink_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(proxy_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/api')

# Gestionnaire d'erreur JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'error': 'Token expiré', 'message': 'Veuillez vous reconnecter'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'error': 'Token invalide', 'message': 'Veuillez vous reconnecter'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'error': 'Token manquant', 'message': 'Authentification requise'}, 401

# Initialisation de la base de données
# Créer les tables automatiquement si elles n'existent pas
with app.app_context():
    try:
        # Vérifier si les tables existent en tentant une requête simple
        from src.models.user import User
        User.query.first()
        print("Base de données déjà initialisée")
    except Exception as e:
        print(f"Initialisation de la base de données nécessaire: {e}")
        db.create_all()
        print("Tables créées avec succès")
    
    # Auto-création et promotion de Denis en superadmin
    try:
        # Chercher l'utilisateur Denis
        denis_user = User.query.filter(
            (User.username == 'Denisadam') | (User.email == 'denis@mdmcmusicads.com')
        ).first()
        
        if denis_user:
            # Utilisateur existe - vérifier s'il est superadmin
            if not denis_user.is_superadmin:
                denis_user.is_superadmin = True
                denis_user.subscription_status = 'active'
                denis_user.is_active = True
                db.session.commit()
                print(f"✅ {denis_user.username} promu en superadmin automatiquement")
            else:
                print(f"ℹ️ {denis_user.username} est déjà superadmin")
        else:
            # Utilisateur n'existe pas - le créer en superadmin
            print("🚀 Création automatique de Denis en superadmin...")
            denis_superadmin = User(
                username='Denisadam',
                email='denis@mdmcmusicads.com',
                is_superadmin=True,
                subscription_status='active',
                is_active=True
            )
            denis_superadmin.set_password('SmartLinks2024!')  # Mot de passe par défaut
            
            db.session.add(denis_superadmin)
            db.session.commit()
            print(f"✅ Denis créé en superadmin avec le mot de passe: SmartLinks2024!")
            print(f"👤 Nom d'utilisateur: Denisadam")
            print(f"📧 Email: denis@mdmcmusicads.com")
            
    except Exception as e:
        db.session.rollback()
        print(f"Info: Gestion Denis superadmin - {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

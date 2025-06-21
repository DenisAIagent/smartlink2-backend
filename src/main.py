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
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
# Nettoyer les espaces
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

print(f"CORS Origins configurées: {cors_origins}")  # Debug en production

CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///test_smartlinks.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Initialisation de la base de données pour le développement
# En production, utilisez flask db upgrade
if os.environ.get('FLASK_ENV') == 'development':
    with app.app_context():
        db.create_all()

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

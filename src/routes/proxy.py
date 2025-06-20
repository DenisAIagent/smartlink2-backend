from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import requests
from urllib.parse import quote
import re

proxy_bp = Blueprint('proxy', __name__)

def is_valid_music_url(url):
    """Valide si l'URL est d'une plateforme musicale connue"""
    music_domains = [
        'spotify.com',
        'music.apple.com',
        'youtube.com',
        'youtu.be',
        'music.youtube.com',
        'soundcloud.com',
        'deezer.com',
        'tidal.com',
        'music.amazon.com',
        'bandcamp.com',
        'audiomack.com',
        'pandora.com'
    ]
    
    return any(domain in url.lower() for domain in music_domains)

@proxy_bp.route('/odesli-proxy', methods=['GET'])
@jwt_required()
def odesli_proxy():
    """Proxy sécurisé pour l'API Odesli (Song.link)"""
    try:
        music_url = request.args.get('url')
        
        # Validation de l'URL
        if not music_url:
            return jsonify({'error': 'Paramètre URL requis'}), 400
        
        music_url = music_url.strip()
        
        # Vérifier le format de l'URL
        if not music_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'URL invalide - doit commencer par http:// ou https://'}), 400
        
        # Vérifier si c'est une URL de plateforme musicale
        if not is_valid_music_url(music_url):
            return jsonify({'error': 'URL non supportée - veuillez utiliser une URL de plateforme musicale valide'}), 400
        
        # Encoder l'URL pour l'API
        encoded_url = quote(music_url, safe='')
        
        # Configuration de la requête
        odesli_url = f"https://api.song.link/v1-alpha.1/links?url={encoded_url}"
        
        headers = {
            'User-Agent': 'SmartLinks-App/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Faire la requête à l'API Odesli
        response = requests.get(
            odesli_url,
            headers=headers,
            timeout=10  # Timeout de 10 secondes
        )
        
        # Vérifier le statut de la réponse
        if response.status_code == 200:
            data = response.json()
            
            # Nettoyer et structurer les données
            cleaned_data = {
                'entityUniqueId': data.get('entityUniqueId'),
                'userCountry': data.get('userCountry'),
                'pageUrl': data.get('pageUrl'),
                'linksByPlatform': data.get('linksByPlatform', {}),
                'entitiesByUniqueId': data.get('entitiesByUniqueId', {})
            }
            
            return jsonify(cleaned_data), 200
            
        elif response.status_code == 404:
            return jsonify({'error': 'Musique non trouvée - cette URL n\'est peut-être pas reconnue par les plateformes de streaming'}), 404
            
        elif response.status_code == 400:
            return jsonify({'error': 'URL invalide ou non supportée'}), 400
            
        else:
            return jsonify({'error': f'Erreur de l\'API Odesli: {response.status_code}'}), 502
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout - l\'API Odesli n\'a pas répondu dans les temps'}), 504
        
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Erreur de connexion - impossible de contacter l\'API Odesli'}), 503
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erreur de requête: {str(e)}'}), 502
        
    except Exception as e:
        return jsonify({'error': f'Erreur interne du serveur: {str(e)}'}), 500

@proxy_bp.route('/validate-music-url', methods=['POST'])
@jwt_required()
def validate_music_url_endpoint():
    """Valide une URL de plateforme musicale"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL requise dans le corps de la requête'}), 400
        
        music_url = data['url'].strip()
        
        # Validation basique
        if not music_url.startswith(('http://', 'https://')):
            return jsonify({
                'valid': False,
                'error': 'URL invalide - doit commencer par http:// ou https://'
            }), 200
        
        # Vérifier si c'est une plateforme musicale
        is_valid = is_valid_music_url(music_url)
        
        return jsonify({
            'valid': is_valid,
            'url': music_url,
            'message': 'URL valide' if is_valid else 'URL de plateforme musicale non reconnue'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur lors de la validation: {str(e)}'}), 500

@proxy_bp.route('/supported-platforms', methods=['GET'])
def get_supported_platforms():
    """Retourne la liste des plateformes musicales supportées"""
    platforms = [
        {
            'name': 'Spotify',
            'domain': 'spotify.com',
            'example': 'https://open.spotify.com/track/...'
        },
        {
            'name': 'Apple Music',
            'domain': 'music.apple.com',
            'example': 'https://music.apple.com/album/...'
        },
        {
            'name': 'YouTube Music',
            'domain': 'music.youtube.com',
            'example': 'https://music.youtube.com/watch?v=...'
        },
        {
            'name': 'YouTube',
            'domain': 'youtube.com',
            'example': 'https://www.youtube.com/watch?v=...'
        },
        {
            'name': 'SoundCloud',
            'domain': 'soundcloud.com',
            'example': 'https://soundcloud.com/artist/track'
        },
        {
            'name': 'Deezer',
            'domain': 'deezer.com',
            'example': 'https://www.deezer.com/track/...'
        },
        {
            'name': 'Tidal',
            'domain': 'tidal.com',
            'example': 'https://tidal.com/browse/track/...'
        },
        {
            'name': 'Amazon Music',
            'domain': 'music.amazon.com',
            'example': 'https://music.amazon.com/albums/...'
        },
        {
            'name': 'Bandcamp',
            'domain': 'bandcamp.com',
            'example': 'https://artist.bandcamp.com/track/...'
        },
        {
            'name': 'Audiomack',
            'domain': 'audiomack.com',
            'example': 'https://audiomack.com/artist/song'
        }
    ]
    
    return jsonify({
        'platforms': platforms,
        'total': len(platforms)
    }), 200

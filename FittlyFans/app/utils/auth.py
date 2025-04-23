from functools import wraps
from flask import request, jsonify
import jwt
from app.config import Config
from app.controllers.usuario_controller import UsuarioController

def token_required(f):
    """Decorador para verificar el token JWT en rutas protegidas."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar si el token está en los headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        try:
            # Decodificar el token
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            # Verificar que el usuario existe
            usuario_controller = UsuarioController()
            usuario = usuario_controller.obtener_por_id(payload['user_id'])
            
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 401
            
            # Añadir el usuario actual a los argumentos de la función
            kwargs['current_user'] = usuario
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def get_user_id_from_token(token):
    """
    Extrae el ID del usuario a partir del token JWT.
    
    Args:
        token: El token JWT
        
    Returns:
        El ID del usuario o None si el token no es válido
    """
    # Implementación dependiendo de cómo almacenas los datos del usuario en el token
    try:
        # Esto es solo un ejemplo, ajústalo según tu implementación
        from flask import current_app
        import jwt
        
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('usuario_id')
    except:
        return None
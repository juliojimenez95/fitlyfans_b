from flask import Blueprint, request, jsonify
import jwt
import datetime
from functools import wraps
from app.config import Config
from app.controllers.usuario_controller import UsuarioController

auth_bp = Blueprint('auth', __name__)
usuario_controller = UsuarioController()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Inicia sesión y genera un token JWT."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No se proporcionaron credenciales'}), 400
    
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    
    if not correo or not contrasena:
        return jsonify({'error': 'Se requiere correo y contraseña'}), 400
    
    # Verificar credenciales
    usuario = usuario_controller.verificar_credenciales(correo, contrasena)
    
    if not usuario:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Generar token JWT
    token_payload = {
        'user_id': usuario['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    
    token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'usuario': usuario
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario y genera un token JWT."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Validar datos requeridos
    required_fields = ['nombre', 'correo', 'contrasena']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # Verificar si el correo ya está registrado
    usuario_existente = usuario_controller.obtener_por_correo(data['correo'])
    if usuario_existente:
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 409
    
    # Crear usuario
    usuario_id = usuario_controller.crear(
        nombre=data['nombre'],
        correo=data['correo'],
        contrasena=data['contrasena'],
        tipo_usuario=data.get('tipo_usuario', 'generico')
    )
    
    if usuario_id == 0:
        return jsonify({'error': 'No se pudo crear el usuario'}), 500
    
    # Obtener el usuario creado
    usuario = usuario_controller.obtener_por_id(usuario_id)
    
    # Generar token JWT
    token_payload = {
        'user_id': usuario['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    }
    
    token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'token': token,
        'usuario': usuario
    }), 201

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # El token debe venir en el encabezado Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        try:
            # Decodificación del token con la verificación de la firma
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], verify=True)
            request.user_id = data['user_id']  # puedes usar esto si necesitas el ID del usuario autenticado
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/usuarios', methods=['GET'])
@token_required
def obtener_usuarios():
    usuarios = usuario_controller.listar_todos()
    return jsonify(usuarios), 200


@auth_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@token_required
def obtener_usuario(usuario_id):
    usuario = usuario_controller.obtener_por_id(usuario_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario), 200

@auth_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@token_required
def actualizar_usuario(usuario_id):
    data = request.json
    if not data:
        return jsonify({'error': 'Datos vacíos'}), 400
    
    actualizado = usuario_controller.actualizar(usuario_id, data)
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar el usuario'}), 500
    
    usuario = usuario_controller.obtener_por_id(usuario_id)
    return jsonify(usuario), 200

@auth_bp.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
@token_required
def eliminar_usuario(usuario_id):
    eliminado = usuario_controller.eliminar(usuario_id)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el usuario'}), 500
    return jsonify({'mensaje': 'Usuario eliminado correctamente'}), 200


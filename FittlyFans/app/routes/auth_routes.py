from flask import Blueprint, request, jsonify
import jwt
import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps
from marshmallow import ValidationError
from app.config import Config
from app.controllers.usuario_controller import UsuarioController
from app.schemas.auth_schemas import LoginSchema, RegistroSchema
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)
usuario_controller = UsuarioController()

@auth_bp.route('/login', methods=['POST'])
@swag_from('../../docs_api/auth/login.yml')
def login():
    """Inicia sesión y genera un token JWT."""
    if not request.is_json:
        return jsonify({'error': 'La petición debe ser JSON'}), 400
        
    try:
        data = LoginSchema().load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Errores de validación', 'detalles': err.messages}), 400
    
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    
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
@swag_from('../../docs_api/auth/register.yml')
def register():
    """Registra un nuevo usuario y genera un token JWT."""
    if not request.is_json:
        return jsonify({'error': 'La petición debe ser JSON'}), 400
        
    try:
        data = RegistroSchema().load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Errores de validación', 'detalles': err.messages}), 400
    
    # Verificar si el correo ya está registrado
    usuario_existente = usuario_controller.obtener_por_correo(data['correo'])
    if usuario_existente:
        return jsonify({'error': 'El correo electrónico ya está registrado'}), 409
    
    # Crear usuario
    usuario_id = usuario_controller.crear(
        nombre=data['nombre'],
        correo=data['correo'],
        contrasena=data['contrasena'],
        tipo_usuario=data.get('tipo_usuario', 'generico'),
        objetivo=data.get('objetivo'),
        nivel_fitness=data.get('nivel_fitness'),
        especialidad=data.get('especialidad'),
        certificaciones=data.get('certificaciones')
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
@swag_from('../../docs_api/auth/obtener_usuarios.yml')
def obtener_usuarios():
    """Obtiene la lista de todos los usuarios"""
    usuarios = usuario_controller.listar_todos()
    return jsonify(usuarios), 200


@auth_bp.route('/usuarios/<int:usuario_id>', methods=['GET'])
@token_required
@swag_from('../../docs_api/auth/obtener_usuario.yml')
def obtener_usuario(usuario_id):
    """Obtiene los detalles de un usuario específico"""
    usuario = usuario_controller.obtener_por_id(usuario_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario), 200

@auth_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
@token_required
@swag_from('../../docs_api/auth/actualizar_usuario.yml')
def actualizar_usuario(usuario_id):
    """Actualiza la información básica del usuario"""
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
@swag_from('../../docs_api/auth/eliminar_usuario.yml')
def eliminar_usuario(usuario_id):
    """Elimina un usuario del sistema atómicamente"""
    eliminado = usuario_controller.eliminar(usuario_id)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el usuario'}), 500
    return jsonify({'mensaje': 'Usuario eliminado correctamente'}), 200

@auth_bp.route('/usuarios/<int:usuario_id>/avatar', methods=['POST'])
@token_required
def subir_avatar(usuario_id):
    """Sube y actualiza el avatar de un usuario"""
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"avatar_{usuario_id}_{timestamp}_{filename}"
        
        # Ensure uploads folder exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        filepath = os.path.join(Config.UPLOAD_FOLDER, new_filename)
        file.save(filepath)
        
        # Guardar ruta relativa para servir desde el backend
        avatar_url = f"/static/uploads/{new_filename}"
        
        actualizado = usuario_controller.actualizar(usuario_id, {'avatar_url': avatar_url})
        if not actualizado:
            return jsonify({'error': 'No se pudo actualizar el avatar'}), 500
            
        usuario = usuario_controller.obtener_por_id(usuario_id)
        return jsonify({'mensaje': 'Avatar actualizado', 'usuario': usuario}), 200
    
    return jsonify({'error': 'Error al procesar el archivo'}), 500


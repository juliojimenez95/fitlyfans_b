from flask import Blueprint, request, jsonify
from app.controllers.entrenador_controller import EntrenadorController
from app.utils.auth import token_required

entrenador_bp = Blueprint('entrenador', __name__)
entrenador_controller = EntrenadorController()

# Crear un nuevo entrenador
@entrenador_bp.route('', methods=['POST'])
@token_required
def crear_entrenador(*args, **kwargs):
    usuario_actual = kwargs['current_user']
    data = request.json

    if not data:
        return jsonify({'error': 'Datos faltantes'}), 400

    usuario_id = data.get('usuario_id', usuario_actual['id'])
    especialidad = data.get('especialidad')
    certificaciones = data.get('certificaciones')

    entrenador = entrenador_controller.obtener(usuario_id)
    if entrenador:
        return jsonify({'error': 'El usuario ya es un entrenador'}), 409

    exito = entrenador_controller.crear(usuario_id, especialidad, certificaciones)

    if not exito:
        return jsonify({'error': 'No se pudo crear el perfil de entrenador'}), 500

    return jsonify({
        'mensaje': 'Perfil de entrenador creado exitosamente',
        'entrenador': entrenador_controller.obtener(usuario_id)
    }), 201

# Obtener un entrenador por ID
@entrenador_bp.route('/<int:entrenador_id>', methods=['GET'])
@token_required
def obtener_entrenador(entrenador_id, *args, **kwargs):
    entrenador = entrenador_controller.obtener(entrenador_id)
    if not entrenador:
        return jsonify({'error': 'Entrenador no encontrado'}), 404
    return jsonify(entrenador), 200

# Actualizar entrenador
@entrenador_bp.route('/<int:entrenador_id>', methods=['PUT'])
@token_required
def actualizar_entrenador(entrenador_id, *args, **kwargs):
    usuario_actual = kwargs['current_user']

    if usuario_actual['id'] != entrenador_id and usuario_actual.get('tipo_usuario') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403

    data = request.json
    if not data:
        return jsonify({'error': 'Datos faltantes'}), 400

    especialidad = data.get('especialidad')
    certificaciones = data.get('certificaciones')

    exito = entrenador_controller.actualizar(entrenador_id, especialidad, certificaciones)

    if not exito:
        return jsonify({'error': 'No se pudo actualizar el perfil'}), 500

    return jsonify({
        'mensaje': 'Perfil actualizado correctamente',
        'entrenador': entrenador_controller.obtener(entrenador_id)
    }), 200

# Listar todos los entrenadores
@entrenador_bp.route('', methods=['GET'])
@token_required
def listar_entrenadores(*args, **kwargs):
    usuario_actual = kwargs['current_user']

   

    limite = request.args.get('limite', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    entrenadores = entrenador_controller.listar_todos(limite, offset)

    return jsonify({
        'total': len(entrenadores),
        'entrenadores': entrenadores
    }), 200

# Buscar por especialidad
@entrenador_bp.route('/buscar', methods=['GET'])
@token_required
def buscar_por_especialidad(*args, **kwargs):
    especialidad = request.args.get('especialidad')
    if not especialidad:
        return jsonify({'error': 'Debe proporcionar una especialidad'}), 400

    entrenadores = entrenador_controller.buscar_por_especialidad(especialidad)
    return jsonify({
        'total': len(entrenadores),
        'entrenadores': entrenadores
    }), 200

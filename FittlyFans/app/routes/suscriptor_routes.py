from flask import Blueprint, request, jsonify
from app.controllers.suscriptor_controller import SuscriptorController
from app.utils.auth import token_required

# Crear blueprint
suscriptor_bp = Blueprint('suscriptor', __name__)
suscriptor_controller = SuscriptorController()

# Ruta para crear un nuevo perfil de suscriptor
@suscriptor_bp.route('', methods=['GET'])
@token_required
def crear_suscriptor(*args, **kwargs):
    usuario_actual = kwargs['current_user']
    data = request.json

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    usuario_id = data.get('usuario_id', usuario_actual['id'])
    objetivo = data.get('objetivo')
    nivel_fitness = data.get('nivel_fitness')

    suscriptor = suscriptor_controller.obtener(usuario_id)
    if suscriptor:
        return jsonify({'error': 'El usuario ya tiene un perfil de suscriptor'}), 409

    exito = suscriptor_controller.crear(
        usuario_id=usuario_id,
        objetivo=objetivo,
        nivel_fitness=nivel_fitness
    )

    if not exito:
        return jsonify({'error': 'No se pudo crear el perfil de suscriptor'}), 500

    suscriptor = suscriptor_controller.obtener(usuario_id)

    return jsonify({
        'mensaje': 'Perfil de suscriptor creado exitosamente',
        'suscriptor': suscriptor
    }), 201

# Ruta para obtener un suscriptor por su ID
@suscriptor_bp.route('/<int:suscriptor_id>', methods=['GET'])
@token_required
def obtener_suscriptor(suscriptor_id, *args, **kwargs):
    suscriptor = suscriptor_controller.obtener(suscriptor_id)

    if not suscriptor:
        return jsonify({'error': 'Suscriptor no encontrado'}), 404

    return jsonify(suscriptor), 200

# Ruta para actualizar un suscriptor
@suscriptor_bp.route('/<int:suscriptor_id>', methods=['PUT'])
@token_required
def actualizar_suscriptor(suscriptor_id, *args, **kwargs):
    usuario_actual = kwargs['current_user']

    if usuario_actual['id'] != suscriptor_id and usuario_actual.get('tipo_usuario') != 'admin':
        return jsonify({'error': 'No autorizado para modificar este perfil'}), 403

    data = request.json
    if not data:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

    objetivo = data.get('objetivo')
    nivel_fitness = data.get('nivel_fitness')

    exito = suscriptor_controller.actualizar(
        suscriptor_id=suscriptor_id,
        objetivo=objetivo,
        nivel_fitness=nivel_fitness
    )

    if not exito:
        return jsonify({'error': 'No se pudo actualizar el perfil de suscriptor'}), 500

    suscriptor = suscriptor_controller.obtener(suscriptor_id)

    return jsonify({
        'mensaje': 'Perfil de suscriptor actualizado exitosamente',
        'suscriptor': suscriptor
    }), 200

# Ruta para listar todos los suscriptores (solo admin o entrenador)
@suscriptor_bp.route('/listar', methods=['GET'])
@token_required
def listar_suscriptores(*args, **kwargs):
    usuario_actual = kwargs['current_user']

    if usuario_actual.get('tipo_usuario') not in ['admin', 'entrenador']:
        return jsonify({'error': 'No autorizado para ver todos los suscriptores'}), 403

    limite = request.args.get('limite', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    nivel_fitness = request.args.get('nivel')

    if nivel_fitness:
        suscriptores = suscriptor_controller.buscar_por_nivel(nivel_fitness, limite)
    else:
        suscriptores = suscriptor_controller.listar_todos(limite, offset)

    return jsonify({
        'total': len(suscriptores),
        'suscriptores': suscriptores
    }), 200

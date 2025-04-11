from flask import Blueprint, request, jsonify
from app.controllers.entrenador_controller import EntrenadorController
from app.utils.auth import token_required

entrenador_bp = Blueprint('entrenador', __name__)
entrenador_controller = EntrenadorController()

@entrenador_bp.route('', methods=['POST'])
@token_required
def crear_entrenador(*args, **kwargs):
    """Crea un nuevo perfil de entrenador para un usuario."""
    usuario_actual = kwargs['current_user']
    data = request.json
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Extraer datos del request
    usuario_id = data.get('usuario_id', usuario_actual['id'])
    especialidad = data.get('especialidad')
    certificaciones = data.get('certificaciones')
    
    # Verificar si el usuario ya tiene un perfil de entrenador
    entrenador = entrenador_controller.obtener(usuario_id)
    if entrenador:
        return jsonify({'error': 'El usuario ya tiene un perfil de entrenador'}), 409
    
    # Crear perfil de entrenador
    exito = entrenador_controller.crear(
        usuario_id=usuario_id,
        especialidad=especialidad,
        certificaciones=certificaciones
    )
    
    if not exito:
        return jsonify({'error': 'No se pudo crear el perfil de entrenador'}), 500
    
    # Obtener el entrenador creado
    entrenador = entrenador_controller.obtener(usuario_id)
    
    return jsonify({
        'mensaje': 'Perfil de entrenador creado exitosamente',
        'entrenador': entrenador
    }), 201

@entrenador_bp.route('/<int:entrenador_id>', methods=['GET'])
@token_required
def obtener_entrenador(entrenador_id, *args, **kwargs):
    """Obtiene la información de un entrenador por su ID."""
    entrenador = entrenador_controller.obtener(entrenador_id)
    
    if not entrenador:
        return jsonify({'error': 'Entrenador no encontrado'}), 404
    
    return jsonify(entrenador), 200

@entrenador_bp.route('/<int:entrenador_id>', methods=['PUT'])
@token_required
def actualizar_entrenador(entrenador_id, *args, **kwargs):
    """Actualiza la información de un entrenador."""
    usuario_actual = kwargs['current_user']
    
    # Verificar si el usuario es el dueño del perfil o un administrador
    if usuario_actual['id'] != entrenador_id and usuario_actual.get('tipo_usuario') != 'admin':
        return jsonify({'error': 'No autorizado para modificar este perfil'}), 403
    
    data = request.json
    if not data:
        return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400
    
    # Extraer datos del request
    especialidad = data.get('especialidad')
    certificaciones = data.get('certificaciones')
    
    # Actualizar perfil de entrenador
    exito = entrenador_controller.actualizar(
        entrenador_id=entrenador_id,
        especialidad=especialidad,
        certificaciones=certificaciones
    )
    
    if not exito:
        return jsonify({'error': 'No se pudo actualizar el perfil de entrenador'}), 500
    
    # Obtener el entrenador actualizado
    entrenador = entrenador_controller.obtener(entrenador_id)
    
    return jsonify({
        'mensaje': 'Perfil de entrenador actualizado exitosamente',
        'entrenador': entrenador
    }), 200

@entrenador_bp.route('', methods=['GET'])
@token_required
def listar_entrenadores(*args, **kwargs):
    """Lista todos los entrenadores con paginación."""
    # Parámetros de paginación
    limite = request.args.get('limite', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Filtrar por especialidad si se proporciona
    especialidad = request.args.get('especialidad')
    
    if especialidad:
        entrenadores = entrenador_controller.buscar_por_especialidad(especialidad, limite)
    else:
        entrenadores = entrenador_controller.listar_todos(limite, offset)
    
    return jsonify({
        'total': len(entrenadores),
        'entrenadores': entrenadores
    }), 200
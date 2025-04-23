from flask import Blueprint, request, jsonify
from app.controllers.suscripcion_controller import SuscripcionController
from app.utils.auth import token_required

suscripcion_bp = Blueprint('suscripcion', __name__)
suscripcion_controller = SuscripcionController()

# Crear suscripción (seguir a alguien)
@suscripcion_bp.route('', methods=['POST'])
@token_required
def seguir_usuario(*args, **kwargs):
    usuario_actual = kwargs['current_user']
    data = request.json

    id_seguido = data.get('id_seguido')

    if not id_seguido:
        return jsonify({'error': 'Falta el ID del usuario a seguir'}), 400

    if usuario_actual['id'] == id_seguido:
        return jsonify({'error': 'No puedes seguirte a ti mismo'}), 400

    resultado = suscripcion_controller.crear(usuario_actual['id'], id_seguido)

    if resultado == 0:
        return jsonify({'error': 'Ya estás siguiendo a este usuario'}), 409

    return jsonify({'mensaje': 'Suscripción creada con éxito', 'id_suscripcion': resultado}), 201

# Eliminar suscripción (dejar de seguir)
@suscripcion_bp.route('', methods=['DELETE'])
@token_required
def dejar_de_seguir(*args, **kwargs):
    usuario_actual = kwargs['current_user']
    data = request.json

    id_seguido = data.get('id_seguido')

    if not id_seguido:
        return jsonify({'error': 'Falta el ID del usuario a dejar de seguir'}), 400

    exito = suscripcion_controller.eliminar(usuario_actual['id'], id_seguido)

    if not exito:
        return jsonify({'error': 'No se pudo eliminar la suscripción'}), 404

    return jsonify({'mensaje': 'Has dejado de seguir al usuario'}), 200

# Verificar si ya sigue a alguien
@suscripcion_bp.route('/verificar', methods=['GET'])
@token_required
def verificar_suscripcion(*args, **kwargs):
    usuario_actual = kwargs['current_user']
    id_seguido = request.args.get('id_seguido', type=int)

    if not id_seguido:
        return jsonify({'error': 'Falta el parámetro id_seguido'}), 400

    sigue = suscripcion_controller.es_seguidor(usuario_actual['id'], id_seguido)
    return jsonify({'sigue': sigue}), 200

# Listar seguidores
@suscripcion_bp.route('/<int:id_usuario>/seguidores', methods=['GET'])
@token_required
def listar_seguidores(id_usuario, *args, **kwargs):
    seguidores = suscripcion_controller.listar_seguidores(id_usuario)
    return jsonify({
        'total': len(seguidores),
        'seguidores': seguidores
    }), 200

# Listar seguidos
@suscripcion_bp.route('/<int:id_usuario>/seguidos', methods=['GET'])
@token_required
def listar_seguidos(id_usuario, *args, **kwargs):
    seguidos = suscripcion_controller.listar_seguidos(id_usuario)
    return jsonify({
        'total': len(seguidos),
        'seguidos': seguidos
    }), 200

# Contar seguidores
@suscripcion_bp.route('/<int:id_usuario>/seguidores/count', methods=['GET'])
@token_required
def contar_seguidores(id_usuario, *args, **kwargs):
    total = suscripcion_controller.contar_seguidores(id_usuario)
    return jsonify({'total_seguidores': total}), 200

# Contar seguidos
@suscripcion_bp.route('/<int:id_usuario>/seguidos/count', methods=['GET'])
@token_required
def contar_seguidos(id_usuario, *args, **kwargs):
    total = suscripcion_controller.contar_seguidos(id_usuario)
    return jsonify({'total_seguidos': total}), 200


# Verificar si un usuario sigue a otro (recibe ambos IDs)
@suscripcion_bp.route('/verificar/doble', methods=['GET'])
@token_required
def verificar_suscripcion_doble(*args, **kwargs):
    id_seguidor = request.args.get('id_seguidor', type=int)
    id_seguido = request.args.get('id_seguido', type=int)

    if not id_seguidor or not id_seguido:
        return jsonify({'error': 'Faltan los parámetros id_seguidor o id_seguido'}), 400

    sigue = suscripcion_controller.es_seguidor(id_seguidor, id_seguido)
    return jsonify({'sigue': sigue}), 200

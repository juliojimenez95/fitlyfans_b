from flask import Blueprint, request, jsonify
from app.controllers.mensaje_Controller import MensajeController
from app.utils.auth import token_required

mensaje_bp = Blueprint('mensaje', __name__)
mensaje_controller = MensajeController()

# Crear un nuevo mensaje
@mensaje_bp.route('', methods=['POST'])
@token_required
def crear_mensaje(current_user):
    data = request.json
    suscriptor_id = data.get('suscriptor_id')
    entrenador_id = data.get('entrenador_id')
    contenido = data.get('contenido')
    emisor = data.get('emisor')  # 0 para entrenador, 1 para suscriptor
    
    if not all([suscriptor_id, entrenador_id, contenido, emisor is not None]):
        return jsonify({'error': 'Suscriptor, entrenador, contenido y emisor son obligatorios'}), 400

    # Verificar que el usuario actual sea el emisor correcto
    if emisor == 1 and current_user['tipo'] != 'suscriptor':
        return jsonify({'error': 'Solo los suscriptores pueden enviar mensajes como suscriptor'}), 403
    if emisor == 0 and current_user['tipo'] != 'entrenador':
        return jsonify({'error': 'Solo los entrenadores pueden enviar mensajes como entrenador'}), 403

    mensaje_id = mensaje_controller.crear(suscriptor_id, entrenador_id, emisor, contenido)
    if not mensaje_id:
        return jsonify({'error': 'No se pudo crear el mensaje'}), 400
    
    return jsonify({'mensaje': 'Mensaje enviado', 'id_mensaje': mensaje_id}), 201

# Obtener mensaje por ID
@mensaje_bp.route('/<int:mensaje_id>', methods=['GET'])
@token_required
def obtener_mensaje(current_user, mensaje_id):
    mensaje = mensaje_controller.obtener(mensaje_id)
    if not mensaje:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    
    # Verificar que el usuario tenga permiso para ver este mensaje
    if current_user['tipo'] == 'suscriptor' and mensaje['suscriptor_id'] != current_user['id']:
        return jsonify({'error': 'No tiene permiso para ver este mensaje'}), 403
    if current_user['tipo'] == 'entrenador' and mensaje['entrenador_id'] != current_user['id']:
        return jsonify({'error': 'No tiene permiso para ver este mensaje'}), 403
    
    return jsonify(mensaje), 200

# Listar mensajes entre un suscriptor y entrenador específicos
@mensaje_bp.route('/entrenador/<int:entrenador_id>/suscriptor/<int:suscriptor_id>', methods=['GET'])
@token_required
def listar_mensajes(current_user, entrenador_id, suscriptor_id):
    # Verificar que el usuario tenga permiso para ver estos mensajes
    if current_user['tipo'] == 'suscriptor' and current_user['id'] != suscriptor_id:
        return jsonify({'error': 'No tiene permiso para ver estos mensajes'}), 403
    if current_user['tipo'] == 'entrenador' and current_user['id'] != entrenador_id:
        return jsonify({'error': 'No tiene permiso para ver estos mensajes'}), 403
    
    limite = int(request.args.get('limite', 100))
    offset = int(request.args.get('offset', 0))
    
    mensajes = mensaje_controller.listar_por_entrenador_suscriptor(entrenador_id, suscriptor_id, limite, offset)
    
    # Marcar como leídos los mensajes que no son del usuario actual
    if current_user['tipo'] == 'suscriptor':
        mensaje_controller.marcar_mensajes_leidos_para_suscriptor(suscriptor_id, entrenador_id)
    else:
        mensaje_controller.marcar_mensajes_leidos_para_entrenador(suscriptor_id, entrenador_id)
    
    return jsonify({'total': len(mensajes), 'mensajes': mensajes}), 200

# Marcar mensaje como leído
@mensaje_bp.route('/<int:mensaje_id>/leido', methods=['PUT'])
@token_required
def marcar_mensaje_leido(current_user, mensaje_id):
    mensaje = mensaje_controller.obtener(mensaje_id)
    if not mensaje:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    
    # Verificar que el usuario tenga permiso para marcar este mensaje
    if current_user['tipo'] == 'suscriptor' and mensaje['suscriptor_id'] != current_user['id']:
        return jsonify({'error': 'No tiene permiso para modificar este mensaje'}), 403
    if current_user['tipo'] == 'entrenador' and mensaje['entrenador_id'] != current_user['id']:
        return jsonify({'error': 'No tiene permiso para modificar este mensaje'}), 403
    
    actualizado = mensaje_controller.marcar_como_leido(mensaje_id)
    if not actualizado:
        return jsonify({'error': 'No se pudo marcar el mensaje como leído'}), 400
    
    return jsonify({'mensaje': 'Mensaje marcado como leído'}), 200

# Marcar todos los mensajes como leídos para un suscriptor y entrenador específicos
@mensaje_bp.route('/entrenador/<int:entrenador_id>/suscriptor/<int:suscriptor_id>/leidos', methods=['PUT'])
@token_required
def marcar_todos_leidos(current_user, entrenador_id, suscriptor_id):
    # Verificar que el usuario tenga permiso para marcar estos mensajes
    if current_user['tipo'] == 'suscriptor' and current_user['id'] != suscriptor_id:
        return jsonify({'error': 'No tiene permiso para modificar estos mensajes'}), 403
    if current_user['tipo'] == 'entrenador' and current_user['id'] != entrenador_id:
        return jsonify({'error': 'No tiene permiso para modificar estos mensajes'}), 403
    
    if current_user['tipo'] == 'suscriptor':
        actualizado = mensaje_controller.marcar_mensajes_leidos_para_suscriptor(suscriptor_id, entrenador_id)
    else:
        actualizado = mensaje_controller.marcar_mensajes_leidos_para_entrenador(suscriptor_id, entrenador_id)
    
    return jsonify({'mensaje': 'Mensajes marcados como leídos', 'actualizados': actualizado}), 200

# Contar mensajes no leídos para el usuario actual
@mensaje_bp.route('/no-leidos/contador', methods=['GET'])
@token_required
def contar_mensajes_no_leidos(current_user):
    if current_user['tipo'] == 'suscriptor':
        total = mensaje_controller.contar_no_leidos_suscriptor(current_user['id'])
    else:
        total = mensaje_controller.contar_no_leidos_entrenador(current_user['id'])
    
    return jsonify({'total_no_leidos': total}), 200

# Eliminar un mensaje
@mensaje_bp.route('/<int:mensaje_id>', methods=['DELETE'])
@token_required
def eliminar_mensaje(current_user, mensaje_id):
    mensaje = mensaje_controller.obtener(mensaje_id)
    
    if not mensaje:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    
    # Verificar que el usuario sea el emisor del mensaje
    is_suscriptor_emisor = mensaje.get('emisor') == 1 and current_user['tipo'] == 'suscriptor' and mensaje.get('suscriptor_id') == current_user['id']
    is_entrenador_emisor = mensaje.get('emisor') == 0 and current_user['tipo'] == 'entrenador' and mensaje.get('entrenador_id') == current_user['id']
    
    if not (is_suscriptor_emisor or is_entrenador_emisor):
        return jsonify({'error': 'No tiene permiso para eliminar este mensaje'}), 403
    
    eliminado = mensaje_controller.eliminar(mensaje_id)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el mensaje'}), 400
    
    return jsonify({'mensaje': 'Mensaje eliminado correctamente'}), 200
from flask import Blueprint, request, jsonify
from app.controllers.conversacion_controller import MensajeController, ConversacionController
from app.utils.auth import token_required

mensajes_bp = Blueprint('mensajes', __name__)
mensaje_controller = MensajeController()
conversacion_controller = ConversacionController()

# Rutas para conversaciones
@mensajes_bp.route('/conversaciones', methods=['POST'])
@token_required
def crear_conversacion(*args, **kwargs):
    """Crea una nueva conversación."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Verificar datos requeridos
    if 'suscriptor_id' not in data or 'entrenador_id' not in data:
        return jsonify({'error': 'Se requiere suscriptor_id y entrenador_id'}), 400
    
    # Crear conversación
    conversacion_id = conversacion_controller.crear(
        suscriptor_id=data['suscriptor_id'],
        entrenador_id=data['entrenador_id']
    )
    
    if conversacion_id == 0:
        return jsonify({'error': 'No se pudo crear la conversación'}), 500
    
    # Obtener la conversación creada
    conversacion = conversacion_controller.obtener_por_id(conversacion_id)
    
    return jsonify({
        'mensaje': 'Conversación creada exitosamente',
        'conversacion': conversacion
    }), 201

@mensajes_bp.route('/conversaciones/suscriptor/<int:suscriptor_id>', methods=['GET'])
@token_required
def listar_conversaciones_suscriptor(usuario_actual, suscriptor_id):
    """Lista todas las conversaciones de un suscriptor."""
    limite = int(request.args.get('limite', 50))
    offset = int(request.args.get('offset', 0))
    
    conversaciones = conversacion_controller.listar_por_suscriptor(
        suscriptor_id=suscriptor_id,
        limite=limite,
        offset=offset
    )
    
    return jsonify({
        'conversaciones': conversaciones,
        'total': len(conversaciones)
    }), 200

@mensajes_bp.route('/conversaciones/entrenador/<int:entrenador_id>', methods=['GET'])
@token_required
def listar_conversaciones_entrenador(usuario_actual, entrenador_id):
    """Lista todas las conversaciones de un entrenador."""
    limite = int(request.args.get('limite', 50))
    offset = int(request.args.get('offset', 0))
    
    conversaciones = conversacion_controller.listar_por_entrenador(
        entrenador_id=entrenador_id,
        limite=limite,
        offset=offset
    )
    
    return jsonify({
        'conversaciones': conversaciones,
        'total': len(conversaciones)
    }), 200

@mensajes_bp.route('/conversaciones/<int:conversacion_id>', methods=['GET'])
@token_required
def obtener_conversacion(usuario_actual, conversacion_id):
    """Obtiene los detalles de una conversación."""
    conversacion = conversacion_controller.obtener_por_id(conversacion_id)
    
    if not conversacion:
        return jsonify({'error': 'Conversación no encontrada'}), 404
    
    return jsonify({
        'conversacion': conversacion
    }), 200

@mensajes_bp.route('/conversaciones/<int:conversacion_id>/estado', methods=['PUT'])
@token_required
def actualizar_estado_conversacion(usuario_actual, conversacion_id):
    """Actualiza el estado de una conversación."""
    data = request.json
    
    if not data or 'estado' not in data:
        return jsonify({'error': 'Se requiere el campo estado'}), 400
    
    estado = data['estado']
    if estado not in ['activa', 'archivada']:
        return jsonify({'error': 'Estado no válido. Debe ser "activa" o "archivada"'}), 400
    
    actualizado = conversacion_controller.actualizar_estado(conversacion_id, estado)
    
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar el estado de la conversación'}), 500
    
    return jsonify({
        'mensaje': 'Estado de conversación actualizado exitosamente'
    }), 200

@mensajes_bp.route('/conversaciones/<int:conversacion_id>', methods=['DELETE'])
@token_required
def eliminar_conversacion(usuario_actual, conversacion_id):
    """Elimina una conversación."""
    eliminado = conversacion_controller.eliminar(conversacion_id)
    
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar la conversación'}), 500
    
    return jsonify({
        'mensaje': 'Conversación eliminada exitosamente'
    }), 200

# Rutas para mensajes
@mensajes_bp.route('/mensajes', methods=['POST'])
@token_required
def crear_mensaje(usuario_actual):
    """Crea un nuevo mensaje."""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400
    
    # Verificar datos requeridos
    required_fields = ['conversacion_id', 'remitente_id', 'contenido']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    # Crear mensaje
    mensaje_id = mensaje_controller.crear(
        conversacion_id=data['conversacion_id'],
        remitente_id=data['remitente_id'],
        contenido=data['contenido']
    )
    
    if mensaje_id == 0:
        return jsonify({'error': 'No se pudo crear el mensaje'}), 500
    
    # Obtener el mensaje creado
    mensaje = mensaje_controller.obtener_por_id(mensaje_id)
    
    return jsonify({
        'mensaje': 'Mensaje enviado exitosamente',
        'datos': mensaje
    }), 201

@mensajes_bp.route('/conversaciones/<int:conversacion_id>/mensajes', methods=['GET'])
@token_required
def listar_mensajes(usuario_actual, conversacion_id):
    """Lista todos los mensajes de una conversación."""
    limite = int(request.args.get('limite', 100))
    offset = int(request.args.get('offset', 0))
    
    # Verificar que la conversación existe
    conversacion = conversacion_controller.obtener_por_id(conversacion_id)
    if not conversacion:
        return jsonify({'error': 'Conversación no encontrada'}), 404
    
    mensajes = mensaje_controller.listar_por_conversacion(
        conversacion_id=conversacion_id,
        limite=limite,
        offset=offset
    )
    
    return jsonify({
        'mensajes': mensajes,
        'total': len(mensajes)
    }), 200

@mensajes_bp.route('/conversaciones/<int:conversacion_id>/marcar-leidos', methods=['PUT'])
@token_required
def marcar_mensajes_leidos(usuario_actual, conversacion_id):
    """Marca como leídos todos los mensajes no enviados por el usuario actual."""
    mensajes_actualizados = mensaje_controller.marcar_como_leidos(
        conversacion_id=conversacion_id,
        usuario_id=usuario_actual['id']
    )
    
    return jsonify({
        'mensaje': 'Mensajes marcados como leídos',
        'mensajes_actualizados': mensajes_actualizados
    }), 200

@mensajes_bp.route('/mensajes/no-leidos', methods=['GET'])
@token_required
def contar_mensajes_no_leidos(usuario_actual):
    """Cuenta el número de mensajes no leídos del usuario actual."""
    total = mensaje_controller.contar_no_leidos(usuario_actual['id'])
    
    return jsonify({
        'total_no_leidos': total
    }), 200

@mensajes_bp.route('/mensajes/<int:mensaje_id>', methods=['DELETE'])
@token_required
def eliminar_mensaje(usuario_actual, mensaje_id):
    """Elimina un mensaje."""
    # Verificar que el mensaje existe y pertenece al usuario
    mensaje = mensaje_controller.obtener_por_id(mensaje_id)
    if not mensaje:
        return jsonify({'error': 'Mensaje no encontrado'}), 404
    
    if mensaje['remitente_id'] != usuario_actual['id']:
        return jsonify({'error': 'No tienes permiso para eliminar este mensaje'}), 403
    
    eliminado = mensaje_controller.eliminar(mensaje_id)
    
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el mensaje'}), 500
    
    return jsonify({
        'mensaje': 'Mensaje eliminado exitosamente'
    }), 200
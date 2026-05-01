from flask_socketio import emit, join_room, leave_room
from flask import request
import jwt
from app.extensions import socketio
from app.config import Config
from app.controllers.mensaje_Controller import MensajeController

mensaje_controller = MensajeController()
# Diccionario para mapear id de usuario con sid (socket id)
connected_users = {}

def decode_token(token):
    try:
        data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], verify=True)
        return data['user_id']
    except Exception:
        return None

@socketio.on('connect')
def handle_connect():
    # Obtener el token de auth (esto dependerá de cómo lo envíe el frontend, usualmente en query string o auth object)
    token = request.args.get('token')
    
    if not token:
        # Se permite la conexión inicial pero no se asigna al usuario
        return True

    user_id = decode_token(token)
    if user_id:
        connected_users[user_id] = request.sid
        # join_room para que el usuario pueda recibir mensajes dirigidos a él
        join_room(f"user_{user_id}")
        print(f"Usuario {user_id} conectado con sid {request.sid}")
    else:
        print("Conexión rechazada: Token inválido")
        return False  # rechaza la conexión

@socketio.on('disconnect')
def handle_disconnect():
    for user_id, sid in list(connected_users.items()):
        if sid == request.sid:
            del connected_users[user_id]
            print(f"Usuario {user_id} desconectado")
            break

@socketio.on('authenticate')
def handle_authenticate(data):
    """Para autenticación manual después de conectar"""
    token = data.get('token')
    if token:
        user_id = decode_token(token)
        if user_id:
            connected_users[user_id] = request.sid
            join_room(f"user_{user_id}")
            print(f"Usuario {user_id} autenticado manualmente")
            emit('authenticated', {'status': 'success'})
            return
    emit('authenticated', {'status': 'error', 'message': 'Invalid token'})

@socketio.on('join_conversation')
def handle_join_conversation(data):
    suscriptor_id = data.get('suscriptor_id')
    entrenador_id = data.get('entrenador_id')
    if suscriptor_id and entrenador_id:
        room_name = f"chat_{suscriptor_id}_{entrenador_id}"
        join_room(room_name)
        print(f"Socket {request.sid} se unió a {room_name}")

@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    suscriptor_id = data.get('suscriptor_id')
    entrenador_id = data.get('entrenador_id')
    if suscriptor_id and entrenador_id:
        room_name = f"chat_{suscriptor_id}_{entrenador_id}"
        leave_room(room_name)

@socketio.on('send_message')
def handle_send_message(data):
    # data debe contener: suscriptor_id, entrenador_id, emisor_id, receptor_id, contenido
    suscriptor_id = data.get('suscriptor_id')
    entrenador_id = data.get('entrenador_id')
    emisor_id = data.get('emisor_id')
    receptor_id = data.get('receptor_id')
    contenido = data.get('contenido')
    
    if not all([suscriptor_id, entrenador_id, emisor_id, receptor_id, contenido]):
        emit('error', {'message': 'Datos incompletos'}, to=request.sid)
        return
        
    try:
        # Guardar en base de datos
        mensaje_id = mensaje_controller.crear(suscriptor_id, entrenador_id, emisor_id, contenido)
        
        if mensaje_id > 0:
            nuevo_mensaje = {
                'id': mensaje_id,
                'id_suscriptor': suscriptor_id,
                'id_entrenador': entrenador_id,
                'emisor': emisor_id,
                'receptor': receptor_id,
                'contenido': contenido,
                'fecha_envio': "Ahora", # El front puede formatearlo
                'estado': 'enviado'
            }
            
            # Crear room unico para este chat: chat_suscriptorID_entrenadorID
            room_name = f"chat_{suscriptor_id}_{entrenador_id}"
            emit('new_message', nuevo_mensaje, room=room_name)
            
            # Opcionalmente, notificar al receptor si no está en la sala pero está conectado
            receptor_sid = connected_users.get(receptor_id)
            if receptor_sid:
                # Se podría enviar un evento de "notificación" general
                emit('message_notification', nuevo_mensaje, room=f"user_{receptor_id}")
                
        else:
            emit('error', {'message': 'No se pudo guardar el mensaje'}, to=request.sid)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        emit('error', {'message': str(e)}, to=request.sid)

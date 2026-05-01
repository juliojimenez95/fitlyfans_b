from flask_socketio import SocketIO

# cors_allowed_origins="*" to allow any frontend to connect during development
socketio = SocketIO(cors_allowed_origins="*")

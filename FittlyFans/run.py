from app import create_app
from app.models.db import DatabaseConnectionSingleton
from app.config import Config

app = create_app()

# ✅ no se mandan parametros porque los toma del .env
db = DatabaseConnectionSingleton()

from app.extensions import socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=Config.DEBUG, allow_unsafe_werkzeug=True)

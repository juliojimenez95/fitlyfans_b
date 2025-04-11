from app import create_app
from app.models.db import DatabaseConnectionSingleton
from app.config import Config

app = create_app()

# ✅ Ya no le pases parámetros, porque los toma del .env
db = DatabaseConnectionSingleton()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)

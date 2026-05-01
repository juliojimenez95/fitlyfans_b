from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from app.config import Config
from app.models import db
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['BASE_URL'] = 'http://127.0.0.1:5000'  # Cambia esto según tu configuración

# Crear directorio si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar SocketIO
    from app.extensions import socketio
    socketio.init_app(app)

    # Importar los eventos de WebSockets (lo crearemos a continuación)
    from app import sockets

    # Configuración de Swagger
    app.config['SWAGGER'] = {
        'title': 'FitlyFans API',
        'uiversion': 3,
        'version': '1.0',
        'description': 'Documentación interactiva de la API Backend de FitlyFans'
    }
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "FitlyFans API",
            "description": "API REST para FitlyFans",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Escribe 'Bearer <token>' en el valor."
            }
        },
    })

    CORS(app) 

    @app.teardown_appcontext
    def close_db_connection(error):
        db.disconnect()

    # Registro de todos los blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.suscriptor_routes import suscriptor_bp
    from app.routes.entrenador_routes import entrenador_bp
    from app.routes.suscripcion_routes import suscripcion_bp
    from app.routes.pago_routes import pago_bp
    from app.routes.experiencia_routes import experiencia_bp
    from app.routes.ejercicio_routes import ejercicio_bp
    from app.routes.rutina_routes import rutina_bp
    from app.routes.contenido_routes import contenido_bp
    from app.routes.comentario_routes import comentario_bp
    from app.routes.progreso_routes import progreso_bp
    from app.routes.conversacion_routes import mensajes_bp
    from app.routes.mensaje_routes import mensaje_bp
    from app.routes.archivo_routes import archivo_bp
    from app.routes.plan_routes import plan_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(suscriptor_bp, url_prefix='/api/suscriptor')
    app.register_blueprint(entrenador_bp, url_prefix='/api/entrenador')
    app.register_blueprint(suscripcion_bp, url_prefix='/api/suscripcion')
    app.register_blueprint(pago_bp, url_prefix='/api/pagos')
    app.register_blueprint(experiencia_bp, url_prefix='/api/experiencias')
    app.register_blueprint(ejercicio_bp, url_prefix='/api/ejercicios')
    app.register_blueprint(rutina_bp, url_prefix='/api/rutina')
    app.register_blueprint(contenido_bp, url_prefix='/api/contenido')
    app.register_blueprint(comentario_bp, url_prefix='/api/comentario')
    app.register_blueprint(mensajes_bp, url_prefix='/api/mensajes')
    app.register_blueprint(mensaje_bp, url_prefix='/api/mensaje')
    app.register_blueprint(archivo_bp, url_prefix='/api/archivos')
    app.register_blueprint(plan_bp, url_prefix='/api/planes')
    app.register_blueprint(progreso_bp, url_prefix='/api/progreso')

    return app

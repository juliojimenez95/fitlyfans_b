from flask import Flask
from flask_cors import CORS  # 👈 AÑADIDO
from app.config import Config
from app.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # 👈 ESTA LÍNEA HABILITA CORS

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

    return app

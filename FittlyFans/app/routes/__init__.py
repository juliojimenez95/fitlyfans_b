from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registro de Blueprints
    from .routes.usuario_routes import usuario_bp
    from .routes.auth_routes import auth_bp  # <--- Asegúrate de tener esta línea
    from .routes.suscriptor_routes import suscriptor_bp

    app.register_blueprint(usuario_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')  # <--- Aquí agregas el blueprint de autenticación
    app.register_blueprint(suscriptor_bp, url_prefix='/api/suscriptor')
    

    return app

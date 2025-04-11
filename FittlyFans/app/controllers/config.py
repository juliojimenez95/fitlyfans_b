import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base para la aplicación."""
    
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    DEBUG = os.environ.get('FLASK_DEBUG') or False
    
    # Configuración de la base de datos
    DB_HOST = os.environ.get('DB_HOST') or '127.0.0.1'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    DB_NAME = os.environ.get('DB_NAME') or 'fittlyfans'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    
    # JWT configuración
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-clave-secreta'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
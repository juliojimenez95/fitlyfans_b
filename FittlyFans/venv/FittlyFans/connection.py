from flask_sqlalchemy import SQLAlchemy

class Database:
    _instance = None
    db = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls.db = SQLAlchemy()
            if app is not None:
                cls.db.init_app(app)
        return cls._instance

    def get_db(self):
        return self.db

# Uso en la aplicación Flask
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost/nombre_base_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos con la aplicación
database = Database(app)
db = database.get_db()

# Definir modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

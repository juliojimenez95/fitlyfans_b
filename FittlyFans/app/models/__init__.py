from ..models.db import DatabaseConnectionSingleton

# Crear una instancia compartida de la base de datos
db = DatabaseConnectionSingleton()

# Función para obtener la conexión a la base de datos
def get_db():
    if not db.connect():
        raise Exception("Error en la conexión a la base de datos")
    return db
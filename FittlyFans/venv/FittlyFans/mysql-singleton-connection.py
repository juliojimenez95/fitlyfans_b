import mysql.connector
from mysql.connector import Error


class DatabaseConnectionSingleton:
    """
    Implementación del patrón Singleton para conexión a MySQL.
    Asegura que solo exista una instancia de la conexión a la base de datos.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """
        Crea una nueva instancia solo si no existe ya una instancia de la clase.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, host="127.0.0.1", port=3306, database="fittlyfans", user="root", password=""):
        """
        Inicializa la configuración de la conexión solo una vez.
        """
        if not hasattr(self, '_initialized') or not self._initialized:
            self.host = host
            self.port = port
            self.database = database
            self.user = user
            self.password = password
            self.connection = None
            self.cursor = None
            self._initialized = True
    
    def connect(self):
        """
        Establece la conexión a la base de datos MySQL.
        """
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                if self.connection.is_connected():
                    self.cursor = self.connection.cursor(dictionary=True)
                    print(f"Conexión exitosa a la base de datos {self.database}")
                    return True
            except Error as e:
                print(f"Error al conectar a MySQL: {e}")
                return False
        return True
    
    def disconnect(self):
        """
        Cierra la conexión a la base de datos MySQL.
        """
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
            print("Conexión cerrada")
    
    def get_connection_id(self):
        """
        Método para verificar que estamos trabajando con la misma instancia.
        Devuelve el ID de la instancia para comparar.
        """
        return id(self)


class DatabaseOperations:
    """
    Clase para realizar operaciones con la base de datos utilizando el Singleton.
    """
    def __init__(self, db_connection=None):
        """
        Inicializa con una conexión a la base de datos o crea una nueva.
        """
        self.db = db_connection if db_connection else DatabaseConnectionSingleton()
    
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL (SELECT) y devuelve los resultados.
        """
        try:
            if not self.db.connect():
                return None
            
            self.db.cursor.execute(query, params or ())
            return self.db.cursor.fetchall()
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """
        Ejecuta una consulta SQL que modifica datos (INSERT, UPDATE, DELETE).
        """
        try:
            if not self.db.connect():
                return -1
            
            self.db.cursor.execute(query, params or ())
            self.db.connection.commit()
            return self.db.cursor.rowcount
        except Error as e:
            print(f"Error al ejecutar la actualización: {e}")
            return -1
    
    def execute_insert(self, query, params=None):
        """
        Ejecuta una consulta SQL de inserción y devuelve el ID generado.
        """
        try:
            if not self.db.connect():
                return -1
            
            self.db.cursor.execute(query, params or ())
            self.db.connection.commit()
            return self.db.cursor.lastrowid
        except Error as e:
            print(f"Error al ejecutar la inserción: {e}")
            return -1


# Ejemplo que demuestra el funcionamiento del patrón Singleton
def test_singleton_pattern():
    """
    Función que demuestra que el patrón Singleton está funcionando correctamente.
    Crea dos instancias y verifica que ambas referencian el mismo objeto.
    """
    print("Prueba del patrón Singleton para la conexión a la base de datos:")
    
    # Crear la primera instancia
    connection1 = DatabaseConnectionSingleton()
    print(f"Primera instancia creada con ID: {connection1.get_connection_id()}")
    
    # Crear la segunda instancia con parámetros diferentes
    # Si el patrón Singleton funciona, esto no debería crear un nuevo objeto
    connection2 = DatabaseConnectionSingleton(host="localhost", password="password123")
    print(f"Segunda instancia creada con ID: {connection2.get_connection_id()}")
    
    # Verificar si ambas instancias referencian el mismo objeto
    if connection1.get_connection_id() == connection2.get_connection_id():
        print("¡El patrón Singleton funciona correctamente! Ambas variables referencian la misma instancia.")
        print(f"Los parámetros de conexión no se modificaron: {connection2.host}, {connection2.password}")
    else:
        print("¡Error! El patrón Singleton no está funcionando correctamente.")
    
    # Probar DatabaseOperations con ambas instancias
    db_ops1 = DatabaseOperations(connection1)
    db_ops2 = DatabaseOperations(connection2)
    
    # Verificar que ambas operaciones usan la misma conexión
    print(f"ID de conexión usada por db_ops1: {db_ops1.db.get_connection_id()}")
    print(f"ID de conexión usada por db_ops2: {db_ops2.db.get_connection_id()}")
    
    if db_ops1.db.get_connection_id() == db_ops2.db.get_connection_id():
        print("¡Confirmado! Ambas instancias de DatabaseOperations usan la misma conexión.")
    else:
        print("¡Error! Las operaciones no están usando la misma conexión.")


# Función para probar la inserción en la base de datos
def test_database_insertion():
    """
    Función que realiza inserciones en la base de datos para comprobar que la conexión funciona.
    """
    print("\n--- PRUEBA DE INSERCIÓN EN LA BASE DE DATOS ---")
    
    # Crear dos instancias diferentes de DatabaseOperations para demostrar el patrón Singleton
    db_ops1 = DatabaseOperations()
    db_ops2 = DatabaseOperations()
    
    # Verificar que ambas instancias son la misma
    print(f"ID de conexión 1: {db_ops1.db.get_connection_id()}")
    print(f"ID de conexión 2: {db_ops2.db.get_connection_id()}")
    print(f"¿Son la misma instancia? {db_ops1.db.get_connection_id() == db_ops2.db.get_connection_id()}")
    
    # 1. Insertar un Usuario
    usuario_query = """
    INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario) 
    VALUES (%s, %s, %s, %s)
    """
    usuario_data = ("Juan Pérez", "juan.perez@example.com", "password123", "entrenador")
    
    usuario_id = db_ops1.execute_insert(usuario_query, usuario_data)
    
    if usuario_id > 0:
        print(f"Usuario insertado con ID: {usuario_id}")
        
        # 2. Insertar un Entrenador
        entrenador_query = """
        INSERT INTO Entrenador (id, especialidad, certificaciones) 
        VALUES (%s, %s, %s)
        """
        entrenador_data = (usuario_id, "Entrenamiento de fuerza", "Certificado NSCA, Especialista en CrossFit")
        
        entrenador_result = db_ops1.execute_update(entrenador_query, entrenador_data)
        
        if entrenador_result > 0:
            print(f"Entrenador insertado correctamente")
            
            # 3. Insertar una Rutina
            rutina_query = """
            INSERT INTO Rutina (id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada) 
            VALUES (%s, %s, %s, %s, %s)
            """
            rutina_data = (
                usuario_id, 
                "Rutina de fuerza básica", 
                "Rutina para principiantes enfocada en desarrollar fuerza en todo el cuerpo", 
                "principiante", 
                45
            )
            
            rutina_id = db_ops2.execute_insert(rutina_query, rutina_data)
            
            if rutina_id > 0:
                print(f"Rutina insertada con ID: {rutina_id}")
                
                # 4. Insertar un Ejercicio
                ejercicio_query = """
                INSERT INTO Ejercicio (nombre, descripcion, grupo_muscular, tipo, video_instruccion) 
                VALUES (%s, %s, %s, %s, %s)
                """
                ejercicio_data = (
                    "Sentadilla", 
                    "Ejercicio básico para trabajar piernas y glúteos", 
                    "piernas", 
                    "fuerza", 
                    "https://ejemplo.com/video/sentadilla"
                )
                
                ejercicio_id = db_ops2.execute_insert(ejercicio_query, ejercicio_data)
                
                if ejercicio_id > 0:
                    print(f"Ejercicio insertado con ID: {ejercicio_id}")
                    
                    # 5. Relacionar Rutina con Ejercicio
                    rutina_ejercicio_query = """
                    INSERT INTO Rutina_Ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, duracion) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    rutina_ejercicio_data = (rutina_id, ejercicio_id, 1, 3, 12, 60)
                    
                    rutina_ejercicio_result = db_ops1.execute_update(rutina_ejercicio_query, rutina_ejercicio_data)
                    
                    if rutina_ejercicio_result > 0:
                        print(f"Ejercicio añadido a la rutina correctamente")
                        
                        # 6. Verificar los datos insertados
                        consulta = f"""
                        SELECT u.nombre, u.correo, e.especialidad, r.nombre as rutina_nombre, 
                               ej.nombre as ejercicio_nombre, re.series, re.repeticiones
                        FROM Usuario u
                        JOIN Entrenador e ON u.id = e.id
                        JOIN Rutina r ON e.id = r.id_entrenador
                        JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
                        JOIN Ejercicio ej ON re.id_ejercicio = ej.id
                        WHERE u.id = {usuario_id}
                        """
                        
                        resultados = db_ops1.execute_query(consulta)
                        
                        if resultados:
                            print("\nDatos insertados verificados:")
                            for row in resultados:
                                print(f"Entrenador: {row['nombre']} ({row['correo']})")
                                print(f"Especialidad: {row['especialidad']}")
                                print(f"Rutina: {row['rutina_nombre']}")
                                print(f"Ejercicio: {row['ejercicio_nombre']}")
                                print(f"Series: {row['series']}, Repeticiones: {row['repeticiones']}")
                        else:
                            print("No se encontraron resultados en la consulta de verificación")
                    else:
                        print("Error al añadir ejercicio a la rutina")
                else:
                    print("Error al insertar ejercicio")
            else:
                print("Error al insertar rutina")
        else:
            print("Error al insertar entrenador")
    else:
        print("Error al insertar usuario")
    
    # Cerrar la conexión
    db_ops1.db.disconnect()


if __name__ == "__main__":
    # Ejecutar la prueba del patrón Singleton
    test_singleton_pattern()
    
    # Ejecutar la prueba de inserción
    test_database_insertion()
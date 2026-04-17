import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class DatabaseConnectionSingleton:
    """
    Implementación del patrón Singleton para conexión a MySQL.
    Asegura que solo exista una instancia de la conexión a la base de datos.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionSingleton, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            # Get database configuration from environment variables
            self.host = os.getenv('DB_HOST', '127.0.0.1')
            self.port = int(os.getenv('DB_PORT', 3306))
            self.database = os.getenv('DB_NAME', 'fittlyfans')
            self.user = os.getenv('DB_USER', 'root')
            self.password = os.getenv('DB_PASSWORD', '')
            
            self.connection = None
            self.cursor = None
            self._initialized = True
    
    def connect(self):
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
                    return True
            except Error as e:
                print(f"Error al conectar a MySQL: {e}")
                raise e
        return True
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None
            print("Conexión cerrada")
            
    def start_transaction(self):
        """Inicia una transacción explícita."""
        self.connect()
        self.connection.start_transaction()
        
    def commit(self):
        """Confirma la transacción actual."""
        if self.connection and self.connection.is_connected():
            self.connection.commit()
            
    def rollback(self):
        """Revierte la transacción actual en caso de error."""
        if self.connection and self.connection.is_connected():
            self.connection.rollback()
    
    def execute_query(self, query: str, params: tuple = None):
        """Ejecuta un SELECT y retorna los resultados."""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error Database execute_query: {e}")
            raise e
    
    def execute_update(self, query: str, params: tuple = None):
        """Ejecuta un UPDATE o DELETE y retorna las filas afectadas. Requiere commit posterior (o externo)."""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            # NOTA: El commit() ahora es responsabilidad del que orqueste la transacción
            return self.cursor.rowcount
        except Error as e:
            print(f"Error Database execute_update: {e}")
            raise e
    
    def execute_insert(self, query: str, params: tuple = None):
        """Ejecuta un INSERT y retorna el ID insertado. Requiere commit posterior (o externo)."""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            # NOTA: El commit() ahora es responsabilidad del que orqueste la transacción
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error Database execute_insert: {e}")
            raise e
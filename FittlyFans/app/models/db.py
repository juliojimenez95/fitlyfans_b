import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

class DatabaseConnectionSingleton:
    """
    Implementación del patrón Singleton para conexión a MySQL.
    Asegura que solo exista un pool de conexiones a la base de datos.
    Cada operación obtiene una conexión del pool y la devuelve, haciéndolo thread-safe.
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
            
            try:
                self.pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="fittlyfans_pool",
                    pool_size=10,
                    pool_reset_session=True,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.user,
                    password=self.password
                )
                print("Pool de conexiones MySQL inicializado correctamente")
            except Error as e:
                print(f"Error al crear pool de MySQL: {e}")
                self.pool = None

            self._initialized = True
    
    def get_connection(self):
        """Obtiene una conexión del pool."""
        if self.pool:
            return self.pool.get_connection()
        raise Exception("El pool de conexiones no está inicializado")
            
    def execute_query(self, query: str, params: tuple = None):
        """Ejecuta un SELECT y retorna los resultados."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            resultados = cursor.fetchall()
            return resultados
        except Error as e:
            print(f"Error Database execute_query: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def execute_update(self, query: str, params: tuple = None):
        """Ejecuta un UPDATE o DELETE y retorna las filas afectadas. Hace commit autómatico."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            rowcount = cursor.rowcount
            conn.commit()
            return rowcount
        except Error as e:
            conn.rollback()
            print(f"Error Database execute_update: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = None):
        """Ejecuta un INSERT y retorna el ID insertado. Hace commit automático."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            lastrowid = cursor.lastrowid
            conn.commit()
            return lastrowid
        except Error as e:
            conn.rollback()
            print(f"Error Database execute_insert: {e}")
            raise e
        finally:
            cursor.close()
            conn.close()
            
    # Mantenemos estos métodos por retrocompatibilidad si alguna parte del código asume estado
    # pero advertimos que su uso ya no es recomendado en la arquitectura de pool.
    def commit(self):
        pass
        
    def rollback(self):
        pass
        
    def disconnect(self):
        pass
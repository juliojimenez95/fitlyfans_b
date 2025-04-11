from typing import List, Dict, Any
from app.models.db import DatabaseConnectionSingleton

class BaseController:
    """Clase base para controladores de entidades."""
    
    def __init__(self):
        """Inicializa con una conexión a la base de datos."""
        self.db = DatabaseConnectionSingleton()
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Método protegido para ejecutar consultas."""
        return self.db.execute_query(query, params)
    
    def _execute_update(self, query: str, params: tuple = None) -> int:
        """Método protegido para ejecutar actualizaciones."""
        return self.db.execute_update(query, params)
    
    def _execute_insert(self, query: str, params: tuple = None) -> int:
        """Método protegido para ejecutar inserciones."""
        return self.db.execute_insert(query, params)
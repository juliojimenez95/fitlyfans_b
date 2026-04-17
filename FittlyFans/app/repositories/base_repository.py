from typing import List, Dict, Any
from app.models.db import DatabaseConnectionSingleton

class BaseRepository:
    """Clase base estandarizada para todos los Repositorios."""
    
    def __init__(self):
        self.db = DatabaseConnectionSingleton()
        
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Ejecuta selects devolviendo un listado de diccionarios."""
        return self.db.execute_query(query, params)
        
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecuta update o delete devolviendo filas afectadas."""
        return self.db.execute_update(query, params)
        
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Ejecuta insert devolviendo el id generado."""
        return self.db.execute_insert(query, params)

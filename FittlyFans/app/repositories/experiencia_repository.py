from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class ExperienciaRepository(BaseRepository):
    """Repositorio para la gestión de Experiencia."""
    
    def crear(self, nombre: str, descripcion: str) -> int:
        query = """
        INSERT INTO Experiencia (nombre, descripcion)
        VALUES (%s, %s)
        """
        return self.execute_insert(query, (nombre, descripcion))
        
    def obtener(self, experiencia_id: int) -> Dict:
        query = "SELECT * FROM Experiencia WHERE id = %s"
        resultados = self.execute_query(query, (experiencia_id,))
        return resultados[0] if resultados else None
        
    def actualizar(self, experiencia_id: int, set_clause: str, valores: list) -> int:
        query = f"UPDATE Experiencia SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def eliminar(self, experiencia_id: int) -> int:
        query = "DELETE FROM Experiencia WHERE id = %s"
        return self.execute_update(query, (experiencia_id,))
        
    def listar_todas(self) -> List[Dict]:
        query = "SELECT * FROM Experiencia ORDER BY nombre"
        return self.execute_query(query)
        
    def buscar(self, termino_busqueda: str) -> List[Dict]:
        query = """
        SELECT * FROM Experiencia 
        WHERE nombre LIKE %s OR descripcion LIKE %s
        ORDER BY nombre
        """
        return self.execute_query(query, (termino_busqueda, termino_busqueda))

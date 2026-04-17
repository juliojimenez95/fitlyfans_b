from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository

class EntrenadorRepository(BaseRepository):
    
    def crear_entrenador(self, usuario_id: int, especialidad: Optional[str], certificaciones: Optional[str]) -> int:
        query = """
        INSERT INTO Entrenador (id, especialidad, certificaciones)
        VALUES (%s, %s, %s)
        """
        return self.execute_insert(query, (usuario_id, especialidad, certificaciones))
        
    def obtener_entrenador_con_usuario(self, entrenador_id: int) -> Optional[Dict]:
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        WHERE e.id = %s
        """
        resultados = self.execute_query(query, (entrenador_id,))
        return resultados[0] if resultados else None
        
    def actualizar_entrenador(self, entrenador_id: int, set_clause: str, valores: list) -> int:
        valores.append(entrenador_id)
        query = f"UPDATE Entrenador SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def listar_todos(self, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        ORDER BY u.id
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limite, offset))
        
    def buscar_por_especialidad(self, termino_busqueda: str, limite: int) -> List[Dict]:
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        WHERE e.especialidad LIKE %s
        ORDER BY u.id
        LIMIT %s
        """
        return self.execute_query(query, (termino_busqueda, limite))

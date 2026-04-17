from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository

class SuscriptorRepository(BaseRepository):
    
    def crear_suscriptor(self, usuario_id: int, objetivo: Optional[str], nivel_fitness: Optional[str]) -> int:
        query = """
        INSERT INTO Suscriptor (id, objetivo, nivel_fitness)
        VALUES (%s, %s, %s)
        """
        return self.execute_insert(query, (usuario_id, objetivo, nivel_fitness))
        
    def obtener_suscriptor_con_usuario(self, suscriptor_id: int) -> Optional[Dict]:
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        WHERE s.id = %s
        """
        resultados = self.execute_query(query, (suscriptor_id,))
        return resultados[0] if resultados else None
        
    def actualizar_suscriptor(self, suscriptor_id: int, set_clause: str, valores: list) -> int:
        valores.append(suscriptor_id)
        query = f"UPDATE Suscriptor SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def listar_todos(self, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        ORDER BY u.id
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (limite, offset))
        
    def buscar_por_nivel(self, nivel: str, limite: int) -> List[Dict]:
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        WHERE s.nivel_fitness = %s
        ORDER BY u.id
        LIMIT %s
        """
        return self.execute_query(query, (nivel, limite))

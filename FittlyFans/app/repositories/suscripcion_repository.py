from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class SuscripcionRepository(BaseRepository):
    """Repositorio para la gestión de Suscripciones."""
    
    def crear(self, id_seguidor: int, id_seguido: int) -> int:
        verificacion = self.execute_query(
            "SELECT id FROM Suscripcion WHERE id_seguidor = %s AND id_seguido = %s",
            (id_seguidor, id_seguido)
        )
        if verificacion:
            return 0
            
        query = """
        INSERT INTO Suscripcion (id_seguidor, id_seguido)
        VALUES (%s, %s)
        """
        return self.execute_insert(query, (id_seguidor, id_seguido))
        
    def eliminar(self, id_seguidor: int, id_seguido: int) -> int:
        query = """
        DELETE FROM Suscripcion 
        WHERE id_seguidor = %s AND id_seguido = %s
        """
        return self.execute_update(query, (id_seguidor, id_seguido))
        
    def es_seguidor(self, id_seguidor: int, id_seguido: int) -> bool:
        query = """
        SELECT id FROM Suscripcion 
        WHERE id_seguidor = %s AND id_seguido = %s
        """
        resultados = self.execute_query(query, (id_seguidor, id_seguido))
        return len(resultados) > 0
        
    def listar_seguidores(self, id_usuario: int) -> List[Dict]:
        query = """
        SELECT u.*, s.fecha_suscripcion
        FROM Suscripcion s
        JOIN Usuario u ON s.id_seguidor = u.id
        WHERE s.id_seguido = %s
        ORDER BY s.fecha_suscripcion DESC
        """
        return self.execute_query(query, (id_usuario,))
        
    def listar_seguidos(self, id_usuario: int) -> List[Dict]:
        query = """
        SELECT u.*, s.fecha_suscripcion
        FROM Suscripcion s
        JOIN Usuario u ON s.id_seguido = u.id
        WHERE s.id_seguidor = %s
        ORDER BY s.fecha_suscripcion DESC
        """
        return self.execute_query(query, (id_usuario,))
        
    def contar_seguidores(self, id_usuario: int) -> int:
        query = "SELECT COUNT(*) as total FROM Suscripcion WHERE id_seguido = %s"
        resultados = self.execute_query(query, (id_usuario,))
        return resultados[0]['total'] if resultados else 0
        
    def contar_seguidos(self, id_usuario: int) -> int:
        query = "SELECT COUNT(*) as total FROM Suscripcion WHERE id_seguidor = %s"
        resultados = self.execute_query(query, (id_usuario,))
        return resultados[0]['total'] if resultados else 0

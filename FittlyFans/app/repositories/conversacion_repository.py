from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class ConversacionRepository(BaseRepository):
    """Repositorio para la gestión de conversaciones."""
    
    def crear(self, suscriptor_id: int, entrenador_id: int) -> int:
        query = """
        INSERT INTO Conversacion (suscriptor_id, entrenador_id, estado)
        VALUES (%s, %s, 'activa')
        """
        return self.execute_insert(query, (suscriptor_id, entrenador_id))
        
    def obtener_por_id(self, conversacion_id: int) -> Dict:
        query = "SELECT * FROM Conversacion WHERE id = %s"
        resultados = self.execute_query(query, (conversacion_id,))
        return resultados[0] if resultados else None
        
    def listar_por_suscriptor(self, suscriptor_id: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as entrenador_nombre 
        FROM Conversacion c
        JOIN Entrenador e ON c.entrenador_id = e.id
        JOIN Usuario u ON e.usuario_id = u.id
        WHERE c.suscriptor_id = %s
        ORDER BY c.fecha_creacion DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (suscriptor_id, limite, offset))
        
    def listar_por_entrenador(self, entrenador_id: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as suscriptor_nombre 
        FROM Conversacion c
        JOIN Suscriptor s ON c.suscriptor_id = s.id
        JOIN Usuario u ON s.usuario_id = u.id
        WHERE c.entrenador_id = %s
        ORDER BY c.fecha_creacion DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (entrenador_id, limite, offset))
        
    def actualizar_estado(self, conversacion_id: int, estado: str) -> int:
        query = "UPDATE Conversacion SET estado = %s WHERE id = %s"
        return self.execute_update(query, (estado, conversacion_id))
        
    def actualizar_ultimo_mensaje(self, conversacion_id: int, ultimo_mensaje: str) -> int:
        query = "UPDATE Conversacion SET ultimo_mensaje = %s WHERE id = %s"
        return self.execute_update(query, (ultimo_mensaje, conversacion_id))
        
    def eliminar_mensajes(self, conversacion_id: int) -> int:
        return self.execute_update("DELETE FROM Mensaje WHERE conversacion_id = %s", (conversacion_id,))
        
    def eliminar(self, conversacion_id: int) -> int:
        return self.execute_update("DELETE FROM Conversacion WHERE id = %s", (conversacion_id,))

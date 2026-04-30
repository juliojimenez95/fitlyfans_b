from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class ComentarioRepository(BaseRepository):
    """Repositorio para la gestión de comentarios."""
    
    def crear(self, id_usuario: int, id_contenido: int, descripcion: str) -> int:
        query = """
        INSERT INTO Comentario (id_usuario, id_contenido, descripcion)
        VALUES (%s, %s, %s)
        """
        return self.execute_insert(query, (id_usuario, id_contenido, descripcion))
        
    def obtener(self, comentario_id: int) -> Dict:
        query = """
        SELECT c.*, u.nombre as nombre_usuario
        FROM Comentario c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id = %s
        """
        resultados = self.execute_query(query, (comentario_id,))
        return resultados[0] if resultados else None
        
    def actualizar(self, comentario_id: int, descripcion: str) -> int:
        query = "UPDATE Comentario SET descripcion = %s WHERE id = %s"
        return self.execute_update(query, (descripcion, comentario_id))
        
    def eliminar(self, comentario_id: int) -> int:
        query = "DELETE FROM Comentario WHERE id = %s"
        return self.execute_update(query, (comentario_id,))
        
    def listar_por_contenido(self, id_contenido: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario
        FROM Comentario c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id_contenido = %s
        ORDER BY c.fecha_comentario DESC
        """
        return self.execute_query(query, (id_contenido,))
        
    def listar_por_usuario(self, id_usuario: int, limite: int) -> List[Dict]:
        query = """
        SELECT c.*, ct.descripcion as descripcion_contenido, ct.tipo as tipo_contenido
        FROM Comentario c
        JOIN Contenido ct ON c.id_contenido = ct.id
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_comentario DESC
        LIMIT %s
        """
        return self.execute_query(query, (id_usuario, limite))

from typing import List, Dict
from app.controllers.base_controller import BaseController
class ComentarioController(BaseController):
    """Controlador para la entidad Comentario."""
    
    def crear(self, id_usuario: int, id_contenido: int, descripcion: str) -> int:
        """
        Crea un nuevo comentario.
        
        Args:
            id_usuario: ID del usuario que comenta
            id_contenido: ID del contenido comentado
            descripcion: Texto del comentario
            
        Returns:
            ID del comentario creado o 0 si falla
        """
        query = """
        INSERT INTO Comentario (id_usuario, id_contenido, descripcion)
        VALUES (%s, %s, %s)
        """
        return self._execute_insert(query, (id_usuario, id_contenido, descripcion))
    
    def obtener(self, comentario_id: int) -> Dict:
        """
        Obtiene un comentario por su ID.
        
        Args:
            comentario_id: ID del comentario
            
        Returns:
            Información del comentario o diccionario vacío si no se encuentra
        """
        query = """
        SELECT c.*, u.nombre as nombre_usuario
        FROM Comentario c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id = %s
        """
        resultados = self._execute_query(query, (comentario_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, comentario_id: int, descripcion: str) -> bool:
        """
        Actualiza el texto de un comentario.
        
        Args:
            comentario_id: ID del comentario
            descripcion: Nuevo texto del comentario
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        query = "UPDATE Comentario SET descripcion = %s WHERE id = %s"
        filas_afectadas = self._execute_update(query, (descripcion, comentario_id))
        return filas_afectadas > 0
    
    def eliminar(self, comentario_id: int) -> bool:
        """
        Elimina un comentario.
        
        Args:
            comentario_id: ID del comentario
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = "DELETE FROM Comentario WHERE id = %s"
        filas_afectadas = self._execute_update(query, (comentario_id,))
        return filas_afectadas > 0
    
    def listar_por_contenido(self, id_contenido: int) -> List[Dict]:
        """
        Lista todos los comentarios de un contenido.
        
        Args:
            id_contenido: ID del contenido
            
        Returns:
            Lista de comentarios del contenido
        """
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario
        FROM Comentario c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id_contenido = %s
        ORDER BY c.fecha_comentario DESC
        """
        return self._execute_query(query, (id_contenido,))
    
    def listar_por_usuario(self, id_usuario: int, limite: int = 50) -> List[Dict]:
        """
        Lista comentarios realizados por un usuario.
        
        Args:
            id_usuario: ID del usuario
            limite: Número máximo de resultados
            
        Returns:
            Lista de comentarios del usuario
        """
        query = """
        SELECT c.*, ct.descripcion as descripcion_contenido, ct.tipo as tipo_contenido
        FROM Comentario c
        JOIN Contenido ct ON c.id_contenido = ct.id
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_comentario DESC
        LIMIT %s
        """
        return self._execute_query(query, (id_usuario, limite))


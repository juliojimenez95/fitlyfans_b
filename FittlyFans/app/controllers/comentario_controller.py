from typing import List, Dict
from app.repositories.comentario_repository import ComentarioRepository

class ComentarioController:
    """Controlador para la entidad Comentario."""
    
    def __init__(self):
        self.comentario_repo = ComentarioRepository()
        
    def crear(self, id_usuario: int, id_contenido: int, descripcion: str) -> int:
        """Crea un nuevo comentario."""
        return self.comentario_repo.crear(id_usuario, id_contenido, descripcion)
    
    def obtener(self, comentario_id: int) -> Dict:
        """Obtiene un comentario por su ID."""
        comentario = self.comentario_repo.obtener(comentario_id)
        return comentario if comentario else {}
    
    def actualizar(self, comentario_id: int, descripcion: str) -> bool:
        """Actualiza el texto de un comentario."""
        filas_afectadas = self.comentario_repo.actualizar(comentario_id, descripcion)
        return filas_afectadas > 0
    
    def eliminar(self, comentario_id: int) -> bool:
        """Elimina un comentario."""
        filas_afectadas = self.comentario_repo.eliminar(comentario_id)
        return filas_afectadas > 0
    
    def listar_por_contenido(self, id_contenido: int) -> List[Dict]:
        """Lista todos los comentarios de un contenido."""
        return self.comentario_repo.listar_por_contenido(id_contenido)
    
    def listar_por_usuario(self, id_usuario: int, limite: int = 50) -> List[Dict]:
        """Lista comentarios realizados por un usuario."""
        return self.comentario_repo.listar_por_usuario(id_usuario, limite)

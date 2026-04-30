from typing import List, Dict
from app.repositories.contenido_repository import ContenidoRepository
from app.models.db import DatabaseConnectionSingleton

class ContenidoController:
    """Controlador para la entidad Contenido."""
    
    def __init__(self):
        self.contenido_repo = ContenidoRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, id_usuario: int, descripcion: str, tipo: str, url_archivo: str = None) -> int:
        """Crea un nuevo contenido."""
        res = self.contenido_repo.crear(id_usuario, descripcion, tipo, url_archivo)
        if res > 0:
            self.db.commit()
        return res
    
    def obtener(self, contenido_id: int) -> Dict:
        """Obtiene un contenido por su ID."""
        contenido = self.contenido_repo.obtener(contenido_id)
        return contenido if contenido else {}
    
    def actualizar(self, contenido_id: int, descripcion: str = None) -> bool:
        """Actualiza la descripción de un contenido."""
        if descripcion is None:
            return False
        filas_afectadas = self.contenido_repo.actualizar(contenido_id, descripcion)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def eliminar(self, contenido_id: int) -> bool:
        """Elimina un contenido y sus comentarios."""
        self.contenido_repo.eliminar_comentarios(contenido_id)
        filas_afectadas = self.contenido_repo.eliminar(contenido_id)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def listar_por_usuario(self, id_usuario: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """Lista todos los contenidos de un usuario."""
        return self.contenido_repo.listar_por_usuario(id_usuario, limite, offset)
    
    def listar_por_tipo(self, tipo: str, limite: int = 50) -> List[Dict]:
        """Lista contenidos por tipo."""
        return self.contenido_repo.listar_por_tipo(tipo, limite)
    
    def buscar(self, termino: str, limite: int = 50) -> List[Dict]:
        """Busca contenidos por descripción."""
        termino_busqueda = f"%{termino}%"
        return self.contenido_repo.buscar(termino_busqueda, limite)

    def listar_feed_suscriptor(self, id_suscriptor: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """Lista el feed de los entrenadores a los que sigue un suscriptor."""
        return self.contenido_repo.listar_feed_suscriptor(id_suscriptor, limite, offset)

    def listar_feed_descubrir(self, id_suscriptor: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """Lista el feed global excluyendo a los entrenadores que ya sigue."""
        return self.contenido_repo.listar_feed_descubrir(id_suscriptor, limite, offset)

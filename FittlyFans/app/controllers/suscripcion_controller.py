from typing import List, Dict
from app.repositories.suscripcion_repository import SuscripcionRepository
from app.models.db import DatabaseConnectionSingleton

class SuscripcionController:
    """Controlador para la entidad Suscripción."""
    
    def __init__(self):
        self.suscripcion_repo = SuscripcionRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, id_seguidor: int, id_seguido: int) -> int:
        res = self.suscripcion_repo.crear(id_seguidor, id_seguido)
        if res > 0:
            self.db.commit()
        return res
    
    def eliminar(self, id_seguidor: int, id_seguido: int) -> bool:
        filas_afectadas = self.suscripcion_repo.eliminar(id_seguidor, id_seguido)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def es_seguidor(self, id_seguidor: int, id_seguido: int) -> bool:
        return self.suscripcion_repo.es_seguidor(id_seguidor, id_seguido)
    
    def listar_seguidores(self, id_usuario: int) -> List[Dict]:
        return self.suscripcion_repo.listar_seguidores(id_usuario)
    
    def listar_seguidos(self, id_usuario: int) -> List[Dict]:
        return self.suscripcion_repo.listar_seguidos(id_usuario)
    
    def contar_seguidores(self, id_usuario: int) -> int:
        return self.suscripcion_repo.contar_seguidores(id_usuario)
    
    def contar_seguidos(self, id_usuario: int) -> int:
        return self.suscripcion_repo.contar_seguidos(id_usuario)

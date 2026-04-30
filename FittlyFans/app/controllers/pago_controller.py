from typing import List, Dict
from app.repositories.pago_repository import PagoRepository
from app.models.db import DatabaseConnectionSingleton

class PagoController:
    """Controlador para la entidad Pago."""
    
    def __init__(self):
        self.pago_repo = PagoRepository()
        self.db = DatabaseConnectionSingleton()
        
    def _validar_estado(self, estado: str) -> bool:
        estados_validos = ['pendiente', 'completado', 'fallido', 'rechazado', 'reembolsado']
        return estado.lower() in estados_validos

    def crear(self, id_suscripcion: int, monto: float, metodo_pago: str, estado: str, descripcion: str) -> int:
        """Crea un nuevo pago."""
        if not self._validar_estado(estado):
            return 0
        res = self.pago_repo.crear(id_suscripcion, monto, metodo_pago, estado, descripcion)
        if res > 0:
            self.db.commit()
        return res
    
    def obtener(self, pago_id: int) -> Dict:
        pago = self.pago_repo.obtener(pago_id)
        return pago if pago else {}
    
    def actualizar_estado(self, pago_id: int, nuevo_estado: str, descripcion: str = None) -> bool:
        filas_afectadas = self.pago_repo.actualizar_estado(pago_id, nuevo_estado, descripcion)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def listar_por_suscriptor(self, id_suscriptor: int) -> List[Dict]:
        return self.pago_repo.listar_por_suscriptor(id_suscriptor)
    
    def listar_por_estado(self, estado: str, limite: int = 100) -> List[Dict]:
        return self.pago_repo.listar_por_estado(estado, limite)
    
    def obtener_estadisticas(self, id_suscriptor: int = None) -> Dict:
        if id_suscriptor:
            return self.pago_repo.obtener_estadisticas_por_suscriptor(id_suscriptor)
        else:
            return self.pago_repo.obtener_estadisticas_globales()

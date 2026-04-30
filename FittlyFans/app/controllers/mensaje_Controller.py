from typing import List, Dict
from app.repositories.mensaje_repository import MensajeRepository
from app.models.db import DatabaseConnectionSingleton

class MensajeController:
    """Controlador para la entidad Mensaje."""
    
    def __init__(self):
        self.mensaje_repo = MensajeRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, suscriptor_id: int, entrenador_id: int, emisor: int, contenido: str) -> int:
        res = self.mensaje_repo.crear_directo(suscriptor_id, entrenador_id, emisor, contenido)
        if res > 0:
            self.db.commit()
        return res
    
    def obtener(self, mensaje_id: int) -> Dict:
        mensaje = self.mensaje_repo.obtener_por_id(mensaje_id)
        return mensaje if mensaje else {}
    
    def actualizar(self, mensaje_id: int, datos: Dict) -> bool:
        campos_permitidos = ["contenido", "leido"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        
        filas_afectadas = self.mensaje_repo.actualizar(mensaje_id, set_clause, valores)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def eliminar(self, mensaje_id: int) -> bool:
        filas_afectadas = self.mensaje_repo.eliminar(mensaje_id)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def listar_por_entrenador_suscriptor(self, entrenador_id: int, suscriptor_id: int, limite: int = 100, offset: int = 0) -> List[Dict]:
        return self.mensaje_repo.listar_por_entrenador_suscriptor(entrenador_id, suscriptor_id, limite, offset)
    
    def marcar_como_leido(self, mensaje_id: int) -> bool:
        filas_afectadas = self.mensaje_repo.marcar_como_leido(mensaje_id)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def marcar_mensajes_leidos_para_suscriptor(self, suscriptor_id: int, entrenador_id: int) -> int:
        res = self.mensaje_repo.marcar_mensajes_leidos_para_suscriptor(suscriptor_id, entrenador_id)
        if res > 0:
            self.db.commit()
        return res
    
    def marcar_mensajes_leidos_para_entrenador(self, suscriptor_id: int, entrenador_id: int) -> int:
        res = self.mensaje_repo.marcar_mensajes_leidos_para_entrenador(suscriptor_id, entrenador_id)
        if res > 0:
            self.db.commit()
        return res
    
    def contar_no_leidos_suscriptor(self, suscriptor_id: int) -> int:
        return self.mensaje_repo.contar_no_leidos_suscriptor(suscriptor_id)
    
    def contar_no_leidos_entrenador(self, entrenador_id: int) -> int:
        return self.mensaje_repo.contar_no_leidos_entrenador(entrenador_id)
        
    def listar_conversaciones_usuario(self, usuario_id: int, tipo_usuario: str) -> List[Dict]:
        return self.mensaje_repo.listar_conversaciones_usuario(usuario_id, tipo_usuario)
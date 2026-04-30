from typing import List, Dict
from app.repositories.conversacion_repository import ConversacionRepository
from app.repositories.mensaje_repository import MensajeRepository

class ConversacionController:
    """Controlador para la entidad Conversacion."""

    def __init__(self):
        self.conversacion_repo = ConversacionRepository()
    
    def crear(self, suscriptor_id: int, entrenador_id: int) -> int:
        return self.conversacion_repo.crear(suscriptor_id, entrenador_id)
    
    def obtener_por_id(self, conversacion_id: int) -> Dict:
        conversacion = self.conversacion_repo.obtener_por_id(conversacion_id)
        return conversacion if conversacion else {}
    
    def listar_por_suscriptor(self, suscriptor_id: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        return self.conversacion_repo.listar_por_suscriptor(suscriptor_id, limite, offset)
    
    def listar_por_entrenador(self, entrenador_id: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        return self.conversacion_repo.listar_por_entrenador(entrenador_id, limite, offset)
    
    def actualizar_estado(self, conversacion_id: int, estado: str) -> bool:
        if estado not in ['activa', 'archivada']:
            return False
        filas_afectadas = self.conversacion_repo.actualizar_estado(conversacion_id, estado)
        return filas_afectadas > 0
    
    def actualizar_ultimo_mensaje(self, conversacion_id: int, ultimo_mensaje: str) -> bool:
        filas_afectadas = self.conversacion_repo.actualizar_ultimo_mensaje(conversacion_id, ultimo_mensaje)
        return filas_afectadas > 0
    
    def eliminar(self, conversacion_id: int) -> bool:
        self.conversacion_repo.eliminar_mensajes(conversacion_id)
        filas_afectadas = self.conversacion_repo.eliminar(conversacion_id)
        return filas_afectadas > 0

class MensajeController:
    """Controlador para la entidad Mensaje (versión de conversación)."""

    def __init__(self):
        self.mensaje_repo = MensajeRepository()
        self.conversacion_controller = ConversacionController()
    
    def crear(self, conversacion_id: int, remitente_id: int, contenido: str) -> int:
        mensaje_id = self.mensaje_repo.crear_en_conversacion(conversacion_id, remitente_id, contenido)
        if mensaje_id > 0:
            self.conversacion_controller.actualizar_ultimo_mensaje(conversacion_id, contenido)
        return mensaje_id
    
    def obtener_por_id(self, mensaje_id: int) -> Dict:
        mensaje = self.mensaje_repo.obtener_por_id(mensaje_id)
        return mensaje if mensaje else {}
    
    def listar_por_conversacion(self, conversacion_id: int, limite: int = 100, offset: int = 0) -> List[Dict]:
        return self.mensaje_repo.listar_por_conversacion(conversacion_id, limite, offset)
    
    def marcar_como_leidos(self, conversacion_id: int, usuario_id: int) -> int:
        return self.mensaje_repo.marcar_como_leidos_en_conversacion(conversacion_id, usuario_id)
    
    def contar_no_leidos(self, usuario_id: int) -> int:
        return self.mensaje_repo.contar_no_leidos_en_conversacion(usuario_id)
    
    def eliminar(self, mensaje_id: int) -> bool:
        filas_afectadas = self.mensaje_repo.eliminar(mensaje_id)
        return filas_afectadas > 0
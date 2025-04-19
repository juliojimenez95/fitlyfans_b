from typing import List, Dict
from app.controllers.base_controller import BaseController

class ConversacionController(BaseController):
    """Controlador para la entidad Conversacion."""

    def __init__(self):
        super().__init__()
    
    def crear(self, suscriptor_id: int, entrenador_id: int) -> int:
        """
        Crea una nueva conversación entre un suscriptor y un entrenador.
        
        Args:
            suscriptor_id: ID del suscriptor
            entrenador_id: ID del entrenador
            
        Returns:
            ID de la conversación creada o 0 si hubo error
        """
        query = """
        INSERT INTO Conversacion (suscriptor_id, entrenador_id, estado)
        VALUES (%s, %s, 'activa')
        """
        return self._execute_insert(query, (suscriptor_id, entrenador_id))
    
    def obtener_por_id(self, conversacion_id: int) -> Dict:
        """
        Obtiene una conversación por su ID.
        
        Args:
            conversacion_id: ID de la conversación a buscar
            
        Returns:
            Información de la conversación o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Conversacion WHERE id = %s"
        resultados = self._execute_query(query, (conversacion_id,))
        return resultados[0] if resultados else {}
    
    def listar_por_suscriptor(self, suscriptor_id: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """
        Lista todas las conversaciones de un suscriptor.
        
        Args:
            suscriptor_id: ID del suscriptor
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de conversaciones
        """
        query = """
        SELECT c.*, u.nombre as entrenador_nombre 
        FROM Conversacion c
        JOIN Entrenador e ON c.entrenador_id = e.id
        JOIN Usuario u ON e.usuario_id = u.id
        WHERE c.suscriptor_id = %s
        ORDER BY c.fecha_creacion DESC
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (suscriptor_id, limite, offset))
    
    def listar_por_entrenador(self, entrenador_id: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """
        Lista todas las conversaciones de un entrenador.
        
        Args:
            entrenador_id: ID del entrenador
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de conversaciones
        """
        query = """
        SELECT c.*, u.nombre as suscriptor_nombre 
        FROM Conversacion c
        JOIN Suscriptor s ON c.suscriptor_id = s.id
        JOIN Usuario u ON s.usuario_id = u.id
        WHERE c.entrenador_id = %s
        ORDER BY c.fecha_creacion DESC
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (entrenador_id, limite, offset))
    
    def actualizar_estado(self, conversacion_id: int, estado: str) -> bool:
        """
        Actualiza el estado de una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            estado: Nuevo estado ('activa' o 'archivada')
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        if estado not in ['activa', 'archivada']:
            return False
            
        query = "UPDATE Conversacion SET estado = %s WHERE id = %s"
        filas_afectadas = self._execute_update(query, (estado, conversacion_id))
        return filas_afectadas > 0
    
    def actualizar_ultimo_mensaje(self, conversacion_id: int, ultimo_mensaje: str) -> bool:
        """
        Actualiza el último mensaje de una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            ultimo_mensaje: Texto del último mensaje
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        query = "UPDATE Conversacion SET ultimo_mensaje = %s WHERE id = %s"
        filas_afectadas = self._execute_update(query, (ultimo_mensaje, conversacion_id))
        return filas_afectadas > 0
    
    def eliminar(self, conversacion_id: int) -> bool:
        """
        Elimina una conversación y todos sus mensajes asociados.
        
        Args:
            conversacion_id: ID de la conversación a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        # Primero eliminar los mensajes asociados
        delete_mensajes = "DELETE FROM Mensaje WHERE conversacion_id = %s"
        self._execute_update(delete_mensajes, (conversacion_id,))
        
        # Luego eliminar la conversación
        delete_conv = "DELETE FROM Conversacion WHERE id = %s"
        filas_afectadas = self._execute_update(delete_conv, (conversacion_id,))
        return filas_afectadas > 0


class MensajeController(BaseController):
    """Controlador para la entidad Mensaje."""

    def __init__(self):
        super().__init__()
        self.conversacion_controller = ConversacionController()
    
    def crear(self, conversacion_id: int, remitente_id: int, contenido: str) -> int:
        """
        Crea un nuevo mensaje en una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            remitente_id: ID del usuario que envía el mensaje
            contenido: Texto del mensaje
            
        Returns:
            ID del mensaje creado o 0 si hubo error
        """
        query = """
        INSERT INTO Mensaje (conversacion_id, remitente_id, contenido, leido)
        VALUES (%s, %s, %s, FALSE)
        """
        mensaje_id = self._execute_insert(query, (conversacion_id, remitente_id, contenido))
        
        if mensaje_id > 0:
            # Actualizar el último mensaje en la conversación
            self.conversacion_controller.actualizar_ultimo_mensaje(conversacion_id, contenido)
        
        return mensaje_id
    
    def obtener_por_id(self, mensaje_id: int) -> Dict:
        """
        Obtiene un mensaje por su ID.
        
        Args:
            mensaje_id: ID del mensaje a buscar
            
        Returns:
            Información del mensaje o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Mensaje WHERE id = %s"
        resultados = self._execute_query(query, (mensaje_id,))
        return resultados[0] if resultados else {}
    
    def listar_por_conversacion(self, conversacion_id: int, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los mensajes de una conversación.
        
        Args:
            conversacion_id: ID de la conversación
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de mensajes
        """
        query = """
        SELECT m.*, u.nombre as remitente_nombre, u.tipo_usuario as tipo_usuario
        FROM Mensaje m
        JOIN Usuario u ON m.remitente_id = u.id
        WHERE m.conversacion_id = %s
        ORDER BY m.fecha_envio
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (conversacion_id, limite, offset))
    
    def marcar_como_leidos(self, conversacion_id: int, usuario_id: int) -> int:
        """
        Marca como leídos todos los mensajes de una conversación que no fueron enviados por el usuario.
        
        Args:
            conversacion_id: ID de la conversación
            usuario_id: ID del usuario que está marcando como leídos
            
        Returns:
            Número de mensajes marcados como leídos
        """
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE conversacion_id = %s AND remitente_id != %s AND leido = FALSE
        """
        return self._execute_update(query, (conversacion_id, usuario_id))
    
    def contar_no_leidos(self, usuario_id: int) -> int:
        """
        Cuenta el número de mensajes no leídos dirigidos a un usuario.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Número de mensajes no leídos
        """
        query = """
        SELECT COUNT(*) as total
        FROM Mensaje m
        JOIN Conversacion c ON m.conversacion_id = c.id
        WHERE m.leido = FALSE AND m.remitente_id != %s
        AND (
            (c.suscriptor_id IN (SELECT id FROM Suscriptor WHERE usuario_id = %s))
            OR 
            (c.entrenador_id IN (SELECT id FROM Entrenador WHERE usuario_id = %s))
        )
        """
        resultado = self._execute_query(query, (usuario_id, usuario_id, usuario_id))
        return resultado[0]["total"] if resultado else 0
    
    def eliminar(self, mensaje_id: int) -> bool:
        """
        Elimina un mensaje.
        
        Args:
            mensaje_id: ID del mensaje a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = "DELETE FROM Mensaje WHERE id = %s"
        filas_afectadas = self._execute_update(query, (mensaje_id,))
        return filas_afectadas > 0
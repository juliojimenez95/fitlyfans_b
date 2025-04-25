from typing import List, Dict
from app.controllers.base_controller import BaseController


class MensajeController(BaseController):
    """Controlador para la entidad Mensaje."""
    
    def crear(self, suscriptor_id: int, entrenador_id: int, emisor: int, contenido: str) -> int:
        """
        Crea un nuevo mensaje.
        
        Args:
            suscriptor_id: ID del suscriptor
            entrenador_id: ID del entrenador
            emisor: 0 si el emisor es el entrenador, 1 si es el suscriptor
            contenido: Contenido del mensaje
            
        Returns:
            ID del mensaje creado o 0 si falla
        """
        query = """
        INSERT INTO Mensaje (suscriptor_id, entrenador_id, emisor, contenido)
        VALUES (%s, %s, %s, %s)
        """
        return self._execute_insert(query, (suscriptor_id, entrenador_id, emisor, contenido))
    
    def obtener(self, mensaje_id: int) -> Dict:
        """
        Obtiene un mensaje por su ID.
        
        Args:
            mensaje_id: ID del mensaje
            
        Returns:
            Información del mensaje o diccionario vacío si no se encuentra
        """
        query = """
        SELECT m.*, 
               CASE 
                   WHEN m.emisor = 1 THEN s.nombre 
                   ELSE e.nombre 
               END as nombre_emisor
        FROM Mensaje m
        LEFT JOIN Suscriptor s ON m.suscriptor_id = s.id
        LEFT JOIN Entrenador e ON m.entrenador_id = e.id
        WHERE m.id = %s
        """
        resultados = self._execute_query(query, (mensaje_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, mensaje_id: int, datos: Dict) -> bool:
        """
        Actualiza los datos de un mensaje.
        
        Args:
            mensaje_id: ID del mensaje a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        campos_permitidos = ["contenido", "leido"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(mensaje_id)
        
        query = f"UPDATE Mensaje SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
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
    
    def listar_por_entrenador_suscriptor(self, entrenador_id: int, suscriptor_id: int, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista mensajes entre un entrenador y un suscriptor con paginación.

        Args:
            entrenador_id: ID del entrenador
            suscriptor_id: ID del suscriptor
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir

        Returns:
            Lista de mensajes
        """
        query = """
        SELECT m.*, 
            CASE 
                WHEN m.emisor = 1 THEN u_sus.nombre 
                ELSE u_ent.nombre 
            END AS nombre_emisor
        FROM Mensaje m
        LEFT JOIN Suscriptor s ON m.suscriptor_id = s.id
        LEFT JOIN Usuario u_sus ON s.id = u_sus.id
        LEFT JOIN Entrenador e ON m.entrenador_id = e.id
        LEFT JOIN Usuario u_ent ON e.id = u_ent.id
        WHERE m.entrenador_id = %s AND m.suscriptor_id = %s
        ORDER BY m.fecha_envio ASC
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (entrenador_id, suscriptor_id, limite, offset))

    
    def marcar_como_leido(self, mensaje_id: int) -> bool:
        """
        Marca un mensaje como leído.
        
        Args:
            mensaje_id: ID del mensaje
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        query = "UPDATE Mensaje SET leido = TRUE WHERE id = %s"
        filas_afectadas = self._execute_update(query, (mensaje_id,))
        return filas_afectadas > 0
    
    def marcar_mensajes_leidos_para_suscriptor(self, suscriptor_id: int, entrenador_id: int) -> int:
        """
        Marca como leídos todos los mensajes enviados por un entrenador a un suscriptor.
        
        Args:
            suscriptor_id: ID del suscriptor receptor
            entrenador_id: ID del entrenador emisor
            
        Returns:
            Número de mensajes actualizados
        """
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE suscriptor_id = %s AND entrenador_id = %s AND emisor = 0 AND leido = FALSE
        """
        filas_afectadas = self._execute_update(query, (suscriptor_id, entrenador_id))
        return filas_afectadas
    
    def marcar_mensajes_leidos_para_entrenador(self, suscriptor_id: int, entrenador_id: int) -> int:
        """
        Marca como leídos todos los mensajes enviados por un suscriptor a un entrenador.
        
        Args:
            suscriptor_id: ID del suscriptor emisor
            entrenador_id: ID del entrenador receptor
            
        Returns:
            Número de mensajes actualizados
        """
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE suscriptor_id = %s AND entrenador_id = %s AND emisor = 1 AND leido = FALSE
        """
        filas_afectadas = self._execute_update(query, (suscriptor_id, entrenador_id))
        return filas_afectadas
    
    def contar_no_leidos_suscriptor(self, suscriptor_id: int) -> int:
        """
        Cuenta los mensajes no leídos para un suscriptor.
        
        Args:
            suscriptor_id: ID del suscriptor
            
        Returns:
            Número de mensajes no leídos
        """
        query = """
        SELECT COUNT(*) as total 
        FROM Mensaje
        WHERE suscriptor_id = %s AND emisor = 0 AND leido = FALSE
        """
        resultados = self._execute_query(query, (suscriptor_id,))
        return resultados[0]['total'] if resultados else 0
    
    def contar_no_leidos_entrenador(self, entrenador_id: int) -> int:
        """
        Cuenta los mensajes no leídos para un entrenador.
        
        Args:
            entrenador_id: ID del entrenador
            
        Returns:
            Número de mensajes no leídos
        """
        query = """
        SELECT COUNT(*) as total 
        FROM Mensaje
        WHERE entrenador_id = %s AND emisor = 1 AND leido = FALSE
        """
        resultados = self._execute_query(query, (entrenador_id,))
        return resultados[0]['total'] if resultados else 0
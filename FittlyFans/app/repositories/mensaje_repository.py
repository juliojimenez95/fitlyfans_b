from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class MensajeRepository(BaseRepository):
    """Repositorio para la gestión de mensajes."""
    
    def crear_en_conversacion(self, conversacion_id: int, remitente_id: int, contenido: str) -> int:
        query = """
        INSERT INTO Mensaje (conversacion_id, remitente_id, contenido, leido)
        VALUES (%s, %s, %s, FALSE)
        """
        return self.execute_insert(query, (conversacion_id, remitente_id, contenido))
        
    def crear_directo(self, suscriptor_id: int, entrenador_id: int, emisor: int, contenido: str) -> int:
        query = """
        INSERT INTO Mensaje (suscriptor_id, entrenador_id, emisor, contenido)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_insert(query, (suscriptor_id, entrenador_id, emisor, contenido))
        
    def obtener_por_id(self, mensaje_id: int) -> Dict:
        query = "SELECT * FROM Mensaje WHERE id = %s"
        resultados = self.execute_query(query, (mensaje_id,))
        return resultados[0] if resultados else None
        
    def listar_por_conversacion(self, conversacion_id: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT m.*, u.nombre as remitente_nombre, u.tipo_usuario as tipo_usuario
        FROM Mensaje m
        JOIN Usuario u ON m.remitente_id = u.id
        WHERE m.conversacion_id = %s
        ORDER BY m.fecha_envio
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (conversacion_id, limite, offset))
        
    def listar_por_entrenador_suscriptor(self, entrenador_id: int, suscriptor_id: int, limite: int, offset: int) -> List[Dict]:
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
        return self.execute_query(query, (entrenador_id, suscriptor_id, limite, offset))
        
    def marcar_como_leidos_en_conversacion(self, conversacion_id: int, usuario_id: int) -> int:
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE conversacion_id = %s AND remitente_id != %s AND leido = FALSE
        """
        return self.execute_update(query, (conversacion_id, usuario_id))
        
    def marcar_como_leido(self, mensaje_id: int) -> int:
        query = "UPDATE Mensaje SET leido = TRUE WHERE id = %s"
        return self.execute_update(query, (mensaje_id,))
        
    def marcar_mensajes_leidos_para_suscriptor(self, suscriptor_id: int, entrenador_id: int) -> int:
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE suscriptor_id = %s AND entrenador_id = %s AND emisor = 0 AND leido = FALSE
        """
        return self.execute_update(query, (suscriptor_id, entrenador_id))
        
    def marcar_mensajes_leidos_para_entrenador(self, suscriptor_id: int, entrenador_id: int) -> int:
        query = """
        UPDATE Mensaje 
        SET leido = TRUE 
        WHERE suscriptor_id = %s AND entrenador_id = %s AND emisor = 1 AND leido = FALSE
        """
        return self.execute_update(query, (suscriptor_id, entrenador_id))
        
    def contar_no_leidos_en_conversacion(self, usuario_id: int) -> int:
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
        resultado = self.execute_query(query, (usuario_id, usuario_id, usuario_id))
        return resultado[0]["total"] if resultado else 0
        
    def contar_no_leidos_suscriptor(self, suscriptor_id: int) -> int:
        query = "SELECT COUNT(*) as total FROM Mensaje WHERE suscriptor_id = %s AND emisor = 0 AND leido = FALSE"
        resultados = self.execute_query(query, (suscriptor_id,))
        return resultados[0]['total'] if resultados else 0
        
    def contar_no_leidos_entrenador(self, entrenador_id: int) -> int:
        query = "SELECT COUNT(*) as total FROM Mensaje WHERE entrenador_id = %s AND emisor = 1 AND leido = FALSE"
        resultados = self.execute_query(query, (entrenador_id,))
        return resultados[0]['total'] if resultados else 0
        
    def eliminar(self, mensaje_id: int) -> int:
        query = "DELETE FROM Mensaje WHERE id = %s"
        return self.execute_update(query, (mensaje_id,))
        
    def actualizar(self, mensaje_id: int, set_clause: str, valores: list) -> int:
        query = f"UPDATE Mensaje SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def listar_conversaciones_usuario(self, usuario_id: int, tipo_usuario: str) -> List[Dict]:
        if tipo_usuario == 'suscriptor':
            query = """
            SELECT m.entrenador_id as otro_usuario_id, u.nombre as otro_usuario_nombre, 
                   m.contenido as ultimo_mensaje, m.fecha_envio, m.leido, m.emisor
            FROM Mensaje m
            JOIN (
                SELECT entrenador_id, MAX(fecha_envio) as max_fecha
                FROM Mensaje
                WHERE suscriptor_id = %s
                GROUP BY entrenador_id
            ) max_m ON m.entrenador_id = max_m.entrenador_id AND m.fecha_envio = max_m.max_fecha
            JOIN Usuario u ON m.entrenador_id = u.id
            WHERE m.suscriptor_id = %s
            ORDER BY m.fecha_envio DESC
            """
        else:
            query = """
            SELECT m.suscriptor_id as otro_usuario_id, u.nombre as otro_usuario_nombre, 
                   m.contenido as ultimo_mensaje, m.fecha_envio, m.leido, m.emisor
            FROM Mensaje m
            JOIN (
                SELECT suscriptor_id, MAX(fecha_envio) as max_fecha
                FROM Mensaje
                WHERE entrenador_id = %s
                GROUP BY suscriptor_id
            ) max_m ON m.suscriptor_id = max_m.suscriptor_id AND m.fecha_envio = max_m.max_fecha
            JOIN Usuario u ON m.suscriptor_id = u.id
            WHERE m.entrenador_id = %s
            ORDER BY m.fecha_envio DESC
            """
        return self.execute_query(query, (usuario_id, usuario_id))

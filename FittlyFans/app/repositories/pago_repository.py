from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class PagoRepository(BaseRepository):
    """Repositorio para la gestión de pagos."""
    
    def crear(self, id_suscripcion: int, monto: float, metodo_pago: str, estado: str, descripcion: str) -> int:
        query = """
        INSERT INTO Pago (id_suscripcion, monto, metodo_pago, estado, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (id_suscripcion, monto, metodo_pago, estado, descripcion))
        
    def obtener(self, pago_id: int) -> Dict:
        query = """
        SELECT p.*, u.nombre as nombre_suscriptor
        FROM Pago p
        JOIN Suscriptor s ON p.id_suscriptor = s.id
        JOIN Usuario u ON s.id = u.id
        WHERE p.id = %s
        """
        resultados = self.execute_query(query, (pago_id,))
        return resultados[0] if resultados else None
        
    def actualizar_estado(self, pago_id: int, nuevo_estado: str, descripcion: str = None) -> int:
        if descripcion is not None:
            query = "UPDATE Pago SET estado = %s, descripcion = %s WHERE id = %s"
            return self.execute_update(query, (nuevo_estado, descripcion, pago_id))
        else:
            query = "UPDATE Pago SET estado = %s WHERE id = %s"
            return self.execute_update(query, (nuevo_estado, pago_id))
            
    def listar_por_suscriptor(self, id_suscriptor: int) -> List[Dict]:
        query = "SELECT * FROM Pago WHERE id_suscriptor = %s ORDER BY fecha_pago DESC"
        return self.execute_query(query, (id_suscriptor,))
        
    def listar_por_estado(self, estado: str, limite: int) -> List[Dict]:
        query = """
        SELECT p.*, u.nombre as nombre_suscriptor
        FROM Pago p
        JOIN Suscriptor s ON p.id_suscriptor = s.id
        JOIN Usuario u ON s.id = u.id
        WHERE p.estado = %s
        ORDER BY p.fecha_pago DESC
        LIMIT %s
        """
        return self.execute_query(query, (estado, limite))
        
    def obtener_estadisticas_por_suscriptor(self, id_suscriptor: int) -> Dict:
        query = """
        SELECT 
            COUNT(*) as total_pagos,
            SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as pagos_completados,
            SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pagos_pendientes,
            SUM(CASE WHEN estado = 'fallido' THEN 1 ELSE 0 END) as pagos_fallidos,
            SUM(CASE WHEN estado = 'completado' THEN monto ELSE 0 END) as total_recaudado
        FROM Pago
        WHERE id_suscriptor = %s
        """
        resultados = self.execute_query(query, (id_suscriptor,))
        return resultados[0] if resultados else {}
        
    def obtener_estadisticas_globales(self) -> Dict:
        query = """
        SELECT 
            COUNT(*) as total_pagos,
            SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as pagos_completados,
            SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pagos_pendientes,
            SUM(CASE WHEN estado = 'fallido' THEN 1 ELSE 0 END) as pagos_fallidos,
            SUM(CASE WHEN estado = 'completado' THEN monto ELSE 0 END) as total_recaudado
        FROM Pago
        """
        resultados = self.execute_query(query)
        return resultados[0] if resultados else {}

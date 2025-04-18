from typing import List, Dict
from app.controllers.base_controller import BaseController


class PagoController(BaseController):
    """Controlador para la entidad Pago."""
    
    def crear(self, pago_id: int, monto: float, metodo_pago: str,
             estado: str = 'pendiente', descripcion: str = None) -> int:
        """
        Registra un nuevo pago.
        
        Args:
            pago_id: ID del suscricion a la que se le hace el pago 
            monto: Monto del pago
            metodo_pago: Método de pago (tarjeta, paypal, transferencia)
            estado: Estado del pago (pendiente, completado, fallido)
            descripcion: Descripción del pago (opcional)
            
        Returns:
            ID del pago creado o 0 si falla
        """
        query = """
        INSERT INTO Pago (pago_id, monto, metodo_pago, estado, descripcion)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self._execute_insert(query, (pago_id, monto, metodo_pago, estado, descripcion))
    
    def obtener(self, pago_id: int) -> Dict:
        """
        Obtiene un pago por su ID.
        
        Args:
            pago_id: ID del pago
            
        Returns:
            Información del pago o diccionario vacío si no se encuentra
        """
        query = """
        SELECT p.*, u.nombre as nombre_suscriptor
        FROM Pago p
        JOIN Suscriptor s ON p.id_suscriptor = s.id
        JOIN Usuario u ON s.id = u.id
        WHERE p.id = %s
        """
        resultados = self._execute_query(query, (pago_id,))
        return resultados[0] if resultados else {}
    
    def actualizar_estado(self, pago_id: int, nuevo_estado: str, descripcion: str = None) -> bool:
        """
        Actualiza el estado de un pago.
        
        Args:
            pago_id: ID del pago
            nuevo_estado: Nuevo estado del pago (pendiente, completado, fallido)
            descripcion: Nueva descripción (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        if descripcion is not None:
            query = """
            UPDATE Pago SET estado = %s, descripcion = %s WHERE id = %s
            """
            filas_afectadas = self._execute_update(query, (nuevo_estado, descripcion, pago_id))
        else:
            query = """
            UPDATE Pago SET estado = %s WHERE id = %s
            """
            filas_afectadas = self._execute_update(query, (nuevo_estado, pago_id))
        
        return filas_afectadas > 0
    
    def listar_por_suscriptor(self, id_suscriptor: int) -> List[Dict]:
        """
        Lista todos los pagos de un suscriptor.
        
        Args:
            id_suscriptor: ID del suscriptor
            
        Returns:
            Lista de pagos del suscriptor
        """
        query = """
        SELECT * FROM Pago 
        WHERE id_suscriptor = %s
        ORDER BY fecha_pago DESC
        """
        return self._execute_query(query, (id_suscriptor,))
    
    def listar_por_estado(self, estado: str, limite: int = 100) -> List[Dict]:
        """
        Lista pagos por estado.
        
        Args:
            estado: Estado de los pagos a buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de pagos con el estado especificado
        """
        query = """
        SELECT p.*, u.nombre as nombre_suscriptor
        FROM Pago p
        JOIN Suscriptor s ON p.id_suscriptor = s.id
        JOIN Usuario u ON s.id = u.id
        WHERE p.estado = %s
        ORDER BY p.fecha_pago DESC
        LIMIT %s
        """
        return self._execute_query(query, (estado, limite))
    
    def obtener_estadisticas(self, id_suscriptor: int = None) -> Dict:
        """
        Obtiene estadísticas de pagos.
        
        Args:
            id_suscriptor: ID del suscriptor (opcional, si se omite se obtienen estadísticas globales)
            
        Returns:
            Diccionario con estadísticas de pagos
        """
        if id_suscriptor:
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
            resultados = self._execute_query(query, (id_suscriptor,))
        else:
            query = """
            SELECT 
                COUNT(*) as total_pagos,
                SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as pagos_completados,
                SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pagos_pendientes,
                SUM(CASE WHEN estado = 'fallido' THEN 1 ELSE 0 END) as pagos_fallidos,
                SUM(CASE WHEN estado = 'completado' THEN monto ELSE 0 END) as total_recaudado
            FROM Pago
            """
            resultados = self._execute_query(query)
        
        return resultados[0] if resultados else {}

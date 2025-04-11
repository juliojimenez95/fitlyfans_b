from typing import List, Dict
from app.controllers.base_controller import BaseController

class SuscripcionController(BaseController):
    """Controlador para la entidad Suscripción (seguidor-seguido)."""
    
    def crear(self, id_seguidor: int, id_seguido: int) -> int:
        """
        Crea una nueva suscripción (un usuario sigue a otro).
        
        Args:
            id_seguidor: ID del usuario que sigue
            id_seguido: ID del usuario seguido
            
        Returns:
            ID de la suscripción creada o 0 si falla
        """
        # Verificar que no exista ya la suscripción
        verificacion = self._execute_query(
            "SELECT id FROM Suscripcion WHERE id_seguidor = %s AND id_seguido = %s",
            (id_seguidor, id_seguido)
        )
        
        if verificacion:
            return 0  # Ya existe la suscripción
        
        query = """
        INSERT INTO Suscripcion (id_seguidor, id_seguido)
        VALUES (%s, %s)
        """
        return self._execute_insert(query, (id_seguidor, id_seguido))
    
    def eliminar(self, id_seguidor: int, id_seguido: int) -> bool:
        """
        Elimina una suscripción (dejar de seguir).
        
        Args:
            id_seguidor: ID del usuario que sigue
            id_seguido: ID del usuario seguido
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = """
        DELETE FROM Suscripcion 
        WHERE id_seguidor = %s AND id_seguido = %s
        """
        filas_afectadas = self._execute_update(query, (id_seguidor, id_seguido))
        return filas_afectadas > 0
    
    def es_seguidor(self, id_seguidor: int, id_seguido: int) -> bool:
        """
        Verifica si un usuario sigue a otro.
        
        Args:
            id_seguidor: ID del posible seguidor
            id_seguido: ID del posible seguido
            
        Returns:
            True si el seguidor sigue al seguido, False en caso contrario
        """
        query = """
        SELECT id FROM Suscripcion 
        WHERE id_seguidor = %s AND id_seguido = %s
        """
        resultados = self._execute_query(query, (id_seguidor, id_seguido))
        return len(resultados) > 0
    
    def listar_seguidores(self, id_usuario: int) -> List[Dict]:
        """
        Lista todos los usuarios que siguen a un usuario.
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Lista de seguidores
        """
        query = """
        SELECT u.*, s.fecha_suscripcion
        FROM Suscripcion s
        JOIN Usuario u ON s.id_seguidor = u.id
        WHERE s.id_seguido = %s
        ORDER BY s.fecha_suscripcion DESC
        """
        return self._execute_query(query, (id_usuario,))
    
    def listar_seguidos(self, id_usuario: int) -> List[Dict]:
        """
        Lista todos los usuarios a los que sigue un usuario.
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Lista de usuarios seguidos
        """
        query = """
        SELECT u.*, s.fecha_suscripcion
        FROM Suscripcion s
        JOIN Usuario u ON s.id_seguido = u.id
        WHERE s.id_seguidor = %s
        ORDER BY s.fecha_suscripcion DESC
        """
        return self._execute_query(query, (id_usuario,))
    
    def contar_seguidores(self, id_usuario: int) -> int:
        """
        Cuenta el número de seguidores de un usuario.
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Número de seguidores
        """
        query = """
        SELECT COUNT(*) as total FROM Suscripcion WHERE id_seguido = %s
        """
        resultados = self._execute_query(query, (id_usuario,))
        return resultados[0]['total'] if resultados else 0
    
    def contar_seguidos(self, id_usuario: int) -> int:
        """
        Cuenta el número de usuarios a los que sigue un usuario.
        
        Args:
            id_usuario: ID del usuario
            
        Returns:
            Número de usuarios seguidos
        """
        query = """
        SELECT COUNT(*) as total FROM Suscripcion WHERE id_seguidor = %s
        """
        resultados = self._execute_query(query, (id_usuario,))
        return resultados[0]['total'] if resultados else 0

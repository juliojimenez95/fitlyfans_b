from typing import List, Dict
from app.controllers.base_controller import BaseController


class SuscriptorController(BaseController):
    """Controlador para la entidad Suscriptor."""
    
    def crear(self, usuario_id: int, objetivo: str = None, nivel_fitness: str = None) -> bool:
        """
        Crea un nuevo suscriptor a partir de un usuario existente.
        
        Args:
            usuario_id: ID del usuario
            objetivo: Objetivo del suscriptor (opcional)
            nivel_fitness: Nivel de fitness (opcional)
            
        Returns:
            True si la creación fue exitosa, False en caso contrario
        """
        query = """
        INSERT INTO Suscriptor (id, objetivo, nivel_fitness)
        VALUES (%s, %s, %s)
        """
        filas_afectadas = self._execute_update(query, (usuario_id, objetivo, nivel_fitness))
        
        # Actualizar tipo de usuario
        if filas_afectadas > 0:
            update_query = """
            UPDATE Usuario SET tipo_usuario = 'suscriptor' WHERE id = %s
            """
            self._execute_update(update_query, (usuario_id,))
        
        return filas_afectadas > 0
    
    def obtener(self, suscriptor_id: int) -> Dict:
        """
        Obtiene la información de un suscriptor y su usuario asociado.
        
        Args:
            suscriptor_id: ID del suscriptor
            
        Returns:
            Información del suscriptor o diccionario vacío si no se encuentra
        """
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        WHERE s.id = %s
        """
        resultados = self._execute_query(query, (suscriptor_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, suscriptor_id: int, objetivo: str = None, nivel_fitness: str = None) -> bool:
        """
        Actualiza los datos de un suscriptor.
        
        Args:
            suscriptor_id: ID del suscriptor
            objetivo: Nuevo objetivo (opcional)
            nivel_fitness: Nuevo nivel de fitness (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        actualizaciones = []
        valores = []
        
        if objetivo is not None:
            actualizaciones.append("objetivo = %s")
            valores.append(objetivo)
        
        if nivel_fitness is not None:
            actualizaciones.append("nivel_fitness = %s")
            valores.append(nivel_fitness)
        
        if not actualizaciones:
            return False
        
        set_clause = ", ".join(actualizaciones)
        valores.append(suscriptor_id)
        
        query = f"UPDATE Suscriptor SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los suscriptores con su información de usuario.
        
        Args:
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de suscriptores
        """
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        ORDER BY u.id
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (limite, offset))
    
    def buscar_por_nivel(self, nivel: str, limite: int = 100) -> List[Dict]:
        """
        Busca suscriptores por nivel de fitness.
        
        Args:
            nivel: Nivel de fitness a buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de suscriptores con el nivel especificado
        """
        query = """
        SELECT u.*, s.objetivo, s.nivel_fitness 
        FROM Suscriptor s
        JOIN Usuario u ON s.id = u.id
        WHERE s.nivel_fitness = %s
        ORDER BY u.id
        LIMIT %s
        """
        return self._execute_query(query, (nivel, limite))

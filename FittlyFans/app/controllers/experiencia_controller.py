from typing import List, Dict
from app.controllers.base_controller import BaseController


class ExperienciaController(BaseController):
    """Controlador para la entidad Experiencia."""
    
    def crear(self, nombre: str, descripcion: str = None) -> int:
        """
        Crea una nueva experiencia.
        
        Args:
            nombre: Nombre de la experiencia
            descripcion: Descripción de la experiencia (opcional)
            
        Returns:
            ID de la experiencia creada o 0 si falla
        """
        query = """
        INSERT INTO Experiencia (nombre, descripcion)
        VALUES (%s, %s)
        """
        return self._execute_insert(query, (nombre, descripcion))
    
    def obtener(self, experiencia_id: int) -> Dict:
        """
        Obtiene una experiencia por su ID.
        
        Args:
            experiencia_id: ID de la experiencia
            
        Returns:
            Información de la experiencia o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Experiencia WHERE id = %s"
        resultados = self._execute_query(query, (experiencia_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, experiencia_id: int, nombre: str = None, descripcion: str = None) -> bool:
        """
        Actualiza los datos de una experiencia.
        
        Args:
            experiencia_id: ID de la experiencia
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        actualizaciones = []
        valores = []
        
        if nombre is not None:
            actualizaciones.append("nombre = %s")
            valores.append(nombre)
        
        if descripcion is not None:
            actualizaciones.append("descripcion = %s")
            valores.append(descripcion)
        
        if not actualizaciones:
            return False
        
        set_clause = ", ".join(actualizaciones)
        valores.append(experiencia_id)
        
        query = f"UPDATE Experiencia SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def eliminar(self, experiencia_id: int) -> bool:
        """
        Elimina una experiencia.
        
        Args:
            experiencia_id: ID de la experiencia
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = "DELETE FROM Experiencia WHERE id = %s"
        filas_afectadas = self._execute_update(query, (experiencia_id,))
        return filas_afectadas > 0
    
    def listar_todas(self) -> List[Dict]:
        """
        Lista todas las experiencias.
        
        Returns:
            Lista de todas las experiencias
        """
        query = "SELECT * FROM Experiencia ORDER BY nombre"
        return self._execute_query(query)
    
    def buscar(self, termino: str) -> List[Dict]:
        """
        Busca experiencias por nombre o descripción.
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de experiencias que coinciden con la búsqueda
        """
        termino_busqueda = f"%{termino}%"
        query = """
        SELECT * FROM Experiencia 
        WHERE nombre LIKE %s OR descripcion LIKE %s
        ORDER BY nombre
        """
        return self._execute_query(query, (termino_busqueda, termino_busqueda))
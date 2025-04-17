from typing import List, Dict
from app.controllers.base_controller import BaseController



class EntrenadorController(BaseController):
    """Controlador para la entidad Entrenador."""
    
    
    def crear(self, usuario_id: int, especialidad: str = None, certificaciones: str = None) -> bool:
        """
        Crea un nuevo entrenador a partir de un usuario existente.
        
        Args:
            usuario_id: ID del usuario
            especialidad: Especialidad del entrenador (opcional)
            certificaciones: Certificaciones del entrenador (opcional)
            
        Returns:
            True si la creación fue exitosa, False en caso contrario
        """
        query = """
        INSERT INTO Entrenador (id, especialidad, certificaciones)
        VALUES (%s, %s, %s)
        """
        filas_afectadas = self._execute_update(query, (usuario_id, especialidad, certificaciones))
        
        # Actualizar tipo de usuario
        if filas_afectadas > 0:
            update_query = """
            UPDATE Usuario SET tipo_usuario = 'entrenador' WHERE id = %s
            """
            self._execute_update(update_query, (usuario_id,))
        
        return filas_afectadas > 0
    
    def obtener(self, entrenador_id: int) -> Dict:
        """
        Obtiene la información de un entrenador y su usuario asociado.
        
        Args:
            entrenador_id: ID del entrenador
            
        Returns:
            Información del entrenador o diccionario vacío si no se encuentra
        """
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        WHERE e.id = %s
        """
        resultados = self._execute_query(query, (entrenador_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, entrenador_id: int, especialidad: str = None, certificaciones: str = None) -> bool:
        """
        Actualiza los datos de un entrenador.
        
        Args:
            entrenador_id: ID del entrenador
            especialidad: Nueva especialidad (opcional)
            certificaciones: Nuevas certificaciones (opcional)
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        actualizaciones = []
        valores = []
        
        if especialidad is not None:
            actualizaciones.append("especialidad = %s")
            valores.append(especialidad)
        
        if certificaciones is not None:
            actualizaciones.append("certificaciones = %s")
            valores.append(certificaciones)
        
        if not actualizaciones:
            return False
        
        set_clause = ", ".join(actualizaciones)
        valores.append(entrenador_id)
        
        query = f"UPDATE Entrenador SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los entrenadores con su información de usuario.
        
        Args:
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de entrenadores
        """
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        ORDER BY u.id
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (limite, offset))
    
    def buscar_por_especialidad(self, especialidad: str, limite: int = 100) -> List[Dict]:
        """
        Busca entrenadores por especialidad.
        
        Args:
            especialidad: Especialidad a buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de entrenadores con la especialidad especificada
        """
        termino_busqueda = f"%{especialidad}%"
        query = """
        SELECT u.*, e.especialidad, e.certificaciones 
        FROM Entrenador e
        JOIN Usuario u ON e.id = u.id
        WHERE e.especialidad LIKE %s
        ORDER BY u.id
        LIMIT %s
        """
        return self._execute_query(query, (termino_busqueda, limite))

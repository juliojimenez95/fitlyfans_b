from typing import List, Dict
from app.controllers.base_controller import BaseController

class ContenidoController(BaseController):
    """Controlador para la entidad Contenido."""
    
    def crear(self, id_usuario: int, descripcion: str, tipo: str) -> int:
        """
        Crea un nuevo contenido.
        
        Args:
            id_usuario: ID del usuario que crea el contenido
            descripcion: Descripción del contenido
            tipo: Tipo de contenido (video, imagen, texto)
            
        Returns:
            ID del contenido creado o 0 si falla
        """
        query = """
        INSERT INTO Contenido (id_usuario, descripcion, tipo)
        VALUES (%s, %s, %s)
        """
        return self._execute_insert(query, (id_usuario, descripcion, tipo))
    
    def obtener(self, contenido_id: int) -> Dict:
        """
        Obtiene un contenido por su ID.
        
        Args:
            contenido_id: ID del contenido
            
        Returns:
            Información del contenido o diccionario vacío si no se encuentra
        """
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id = %s
        """
        resultados = self._execute_query(query, (contenido_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, contenido_id: int, descripcion: str = None) -> bool:
        """
        Actualiza la descripción de un contenido.
        
        Args:
            contenido_id: ID del contenido
            descripcion: Nueva descripción
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        query = "UPDATE Contenido SET descripcion = %s WHERE id = %s"
        filas_afectadas = self._execute_update(query, (descripcion, contenido_id))
        return filas_afectadas > 0
    
    def eliminar(self, contenido_id: int) -> bool:
        """
        Elimina un contenido y sus comentarios.
        
        Args:
            contenido_id: ID del contenido
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        # Eliminar comentarios relacionados
        self._execute_update("DELETE FROM Comentario WHERE id_contenido = %s", (contenido_id,))
        
        # Eliminar el contenido
        query = "DELETE FROM Contenido WHERE id = %s"
        filas_afectadas = self._execute_update(query, (contenido_id,))
        return filas_afectadas > 0
    
    def listar_por_usuario(self, id_usuario: int, limite: int = 50, offset: int = 0) -> List[Dict]:
        """
        Lista todos los contenidos de un usuario.
        
        Args:
            id_usuario: ID del usuario
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de contenidos del usuario
        """
        query = """
        SELECT c.*, 
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s OFFSET %s
        """
        return self._execute_query(query, (id_usuario, limite, offset))
    
    def listar_por_tipo(self, tipo: str, limite: int = 50) -> List[Dict]:
        """
        Lista contenidos por tipo.
        
        Args:
            tipo: Tipo de contenido (video, imagen, texto)
            limite: Número máximo de resultados
            
        Returns:
            Lista de contenidos del tipo especificado
        """
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.tipo = %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s
        """
        return self._execute_query(query, (tipo, limite))
    
    def buscar(self, termino: str, limite: int = 50) -> List[Dict]:
        """
        Busca contenidos por descripción.
        
        Args:
            termino: Término de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de contenidos que coinciden con la búsqueda
        """
        termino_busqueda = f"%{termino}%"
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.descripcion LIKE %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s
        """
        return self._execute_query(query, (termino_busqueda, limite))

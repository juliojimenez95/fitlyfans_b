from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class ContenidoRepository(BaseRepository):
    """Repositorio para la gestión de contenido."""
    
    def crear(self, id_usuario: int, descripcion: str, tipo: str, url_archivo: str = None) -> int:
        query = """
        INSERT INTO Contenido (id_usuario, descripcion, tipo, url_archivo)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_insert(query, (id_usuario, descripcion, tipo, url_archivo))
        
    def obtener(self, contenido_id: int) -> Dict:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.id = %s
        """
        resultados = self.execute_query(query, (contenido_id,))
        return resultados[0] if resultados else None
        
    def actualizar(self, contenido_id: int, descripcion: str) -> int:
        query = "UPDATE Contenido SET descripcion = %s WHERE id = %s"
        return self.execute_update(query, (descripcion, contenido_id))
        
    def eliminar_comentarios(self, contenido_id: int) -> int:
        return self.execute_update("DELETE FROM Comentario WHERE id_contenido = %s", (contenido_id,))
        
    def eliminar(self, contenido_id: int) -> int:
        return self.execute_update("DELETE FROM Contenido WHERE id = %s", (contenido_id,))
        
    def listar_por_usuario(self, id_usuario: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT c.*, 
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        WHERE c.id_usuario = %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (id_usuario, limite, offset))
        
    def listar_por_tipo(self, tipo: str, limite: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.tipo = %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s
        """
        return self.execute_query(query, (tipo, limite))
        
    def buscar(self, termino_busqueda: str, limite: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE c.descripcion LIKE %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s
        """
        return self.execute_query(query, (termino_busqueda, limite))

    def listar_feed_suscriptor(self, id_suscriptor: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario, u.avatar_url,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        JOIN Suscripcion s ON s.id_seguido = u.id
        WHERE s.id_seguidor = %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s OFFSET %s
        """
        return self.execute_query(query, (id_suscriptor, limite, offset))

    def listar_feed_descubrir(self, id_suscriptor: int, limite: int, offset: int) -> List[Dict]:
        query = """
        SELECT c.*, u.nombre as nombre_usuario, u.tipo_usuario, u.avatar_url,
               (SELECT COUNT(*) FROM Comentario WHERE id_contenido = c.id) as num_comentarios
        FROM Contenido c
        JOIN Usuario u ON c.id_usuario = u.id
        WHERE u.id NOT IN (SELECT id_seguido FROM Suscripcion WHERE id_seguidor = %s)
        AND u.id != %s
        ORDER BY c.fecha_publicacion DESC
        LIMIT %s OFFSET %s
        """
        # Excluimos a los que ya sigo, y me excluyo a mi mismo por si acaso soy entrenador
        return self.execute_query(query, (id_suscriptor, id_suscriptor, limite, offset))

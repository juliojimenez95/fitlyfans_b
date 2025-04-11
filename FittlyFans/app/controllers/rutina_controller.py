from typing import List, Dict
from app.controllers.base_controller import BaseController


class RutinaController(BaseController):
    """Controlador para la entidad Rutina."""
    
    def crear(self, id_entrenador: int, nombre: str, descripcion: str = None, 
             nivel_dificultad: str = 'principiante', duracion_estimada: int = 0) -> int:
        """
        Crea una nueva rutina.
        
        Args:
            id_entrenador: ID del entrenador que crea la rutina
            nombre: Nombre de la rutina
            descripcion: Descripción de la rutina (opcional)
            nivel_dificultad: Nivel de dificultad (principiante, intermedio, avanzado)
            duracion_estimada: Duración estimada en minutos
            
        Returns:
            ID de la rutina creada o 0 si falla
        """
        query = """
        INSERT INTO Rutina (id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self._execute_insert(query, (id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada))
    
    def obtener(self, rutina_id: int) -> Dict:
        """
        Obtiene una rutina por su ID.
        
        Args:
            rutina_id: ID de la rutina
            
        Returns:
            Información de la rutina o diccionario vacío si no se encuentra
        """
        query = """
        SELECT r.*, u.nombre as nombre_entrenador, 
               COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        JOIN Entrenador e ON r.id_entrenador = e.id
        JOIN Usuario u ON e.id = u.id
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE r.id = %s
        GROUP BY r.id
        """
        resultados = self._execute_query(query, (rutina_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, rutina_id: int, datos: Dict) -> bool:
        """
        Actualiza los datos de una rutina.
        
        Args:
            rutina_id: ID de la rutina a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        campos_permitidos = ["nombre", "descripcion", "nivel_dificultad", "duracion_estimada"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(rutina_id)
        
        query = f"UPDATE Rutina SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def eliminar(self, rutina_id: int) -> bool:
        """
        Elimina una rutina y sus relaciones con ejercicios.
        
        Args:
            rutina_id: ID de la rutina a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        # Primero eliminar las relaciones en Rutina_Ejercicio
        self._execute_update("DELETE FROM Rutina_Ejercicio WHERE id_rutina = %s", (rutina_id,))
        
        # Luego eliminar la rutina
        query = "DELETE FROM Rutina WHERE id = %s"
        filas_afectadas = self._execute_update(query, (rutina_id,))
        return filas_afectadas > 0
    
    def listar_por_entrenador(self, entrenador_id: int) -> List[Dict]:
        """
        Lista todas las rutinas creadas por un entrenador.
        
        Args:
            entrenador_id: ID del entrenador
            
        Returns:
            Lista de rutinas del entrenador
        """
        query = """
        SELECT r.*, COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE r.id_entrenador = %s
        GROUP BY r.id
        ORDER BY r.id
        """
        return self._execute_query(query, (entrenador_id,))
    
    def listar_por_nivel(self, nivel_dificultad: str, limite: int = 100) -> List[Dict]:
        """
        Lista rutinas por nivel de dificultad.
        
        Args:
            nivel_dificultad: Nivel de dificultad a buscar
            limite: Número máximo de resultados
            
        Returns:
            Lista de rutinas con el nivel especificado
        """
        query = """
        SELECT r.*, u.nombre as nombre_entrenador, 
               COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        JOIN Entrenador e ON r.id_entrenador = e.id
        JOIN Usuario u ON e.id = u.id
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE r.nivel_dificultad = %s
        GROUP BY r.id
        ORDER BY r.id
        LIMIT %s
        """
        return self._execute_query(query, (nivel_dificultad, limite))
    
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        """
        Busca rutinas por nombre o descripción.
        
        Args:
            termino: Término de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de rutinas que coinciden con la búsqueda
        """
        termino_busqueda = f"%{termino}%"
        query = """
        SELECT r.*, u.nombre as nombre_entrenador, 
               COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        JOIN Entrenador e ON r.id_entrenador = e.id
        JOIN Usuario u ON e.id = u.id
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE r.nombre LIKE %s OR r.descripcion LIKE %s
        GROUP BY r.id
        ORDER BY r.id
        LIMIT %s
        """
        return self._execute_query(query, (termino_busqueda, termino_busqueda, limite))

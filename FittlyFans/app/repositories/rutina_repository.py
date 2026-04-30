from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class RutinaRepository(BaseRepository):
    """Repositorio para la gestión de rutinas."""
    
    def crear(self, id_entrenador: int, nombre: str, descripcion: str, nivel_dificultad: str, duracion_estimada: int) -> int:
        query = """
        INSERT INTO Rutina (id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada))
        
    def obtener(self, rutina_id: int) -> Dict:
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
        resultados = self.execute_query(query, (rutina_id,))
        return resultados[0] if resultados else None
        
    def actualizar(self, rutina_id: int, set_clause: str, valores: list) -> int:
        query = f"UPDATE Rutina SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def eliminar_relaciones_ejercicios(self, rutina_id: int) -> int:
        return self.execute_update("DELETE FROM Rutina_Ejercicio WHERE id_rutina = %s", (rutina_id,))
        
    def eliminar(self, rutina_id: int) -> int:
        return self.execute_update("DELETE FROM Rutina WHERE id = %s", (rutina_id,))
        
    def listar_por_entrenador(self, entrenador_id: int, limite: int = 10, offset: int = 0, busqueda: str = "", dificultad: str = "todas") -> List[Dict]:
        query = """
        SELECT r.*, COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE r.id_entrenador = %s
        """
        params = [entrenador_id]
        
        if busqueda:
            query += " AND (r.nombre LIKE %s OR r.descripcion LIKE %s)"
            termino = f"%{busqueda}%"
            params.extend([termino, termino])
            
        if dificultad and dificultad != "todas":
            query += " AND r.nivel_dificultad = %s"
            params.append(dificultad)
            
        query += """
        GROUP BY r.id
        ORDER BY r.id DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limite, offset])
        
        return self.execute_query(query, tuple(params))
        
    def listar_por_nivel(self, nivel_dificultad: str, limite: int) -> List[Dict]:
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
        return self.execute_query(query, (nivel_dificultad, limite))
        
    def buscar(self, termino_busqueda: str, limite: int) -> List[Dict]:
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
        return self.execute_query(query, (termino_busqueda, termino_busqueda, limite))

    def obtener_con_ejercicios(self, rutina_id: int) -> Dict:
        rutina = self.obtener(rutina_id)
        if not rutina:
            return None
            
        query_ejercicios = """
        SELECT e.*, re.series, re.repeticiones, re.orden, re.duracion as duracion_descanso
        FROM Rutina_Ejercicio re
        JOIN Ejercicio e ON re.id_ejercicio = e.id
        WHERE re.id_rutina = %s
        ORDER BY re.orden ASC
        """
        ejercicios = self.execute_query(query_ejercicios, (rutina_id,))
        rutina['ejercicios'] = ejercicios
        return rutina
        
    def listar_feed_suscriptor(self, id_suscriptor: int) -> List[Dict]:
        query = """
        SELECT r.*, u.nombre as nombre_entrenador, 
               COUNT(re.id_ejercicio) as total_ejercicios
        FROM Rutina r
        JOIN Suscripcion s ON r.id_entrenador = s.id_seguido
        JOIN Entrenador e ON r.id_entrenador = e.id
        JOIN Usuario u ON e.id = u.id
        LEFT JOIN Rutina_Ejercicio re ON r.id = re.id_rutina
        WHERE s.id_seguidor = %s
        GROUP BY r.id
        ORDER BY r.id DESC
        """
        return self.execute_query(query, (id_suscriptor,))

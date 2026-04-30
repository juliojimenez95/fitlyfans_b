from typing import List, Dict
from app.repositories.base_repository import BaseRepository

class EjercicioRepository(BaseRepository):
    """Repositorio para la gestión de datos de Ejercicios."""
    
    def crear(self, nombre: str, descripcion: str, grupo_muscular: str, tipo: str, video_instruccion: str, entrenador_id: int) -> int:
        query = """
        INSERT INTO Ejercicio (nombre, descripcion, grupo_muscular, tipo, video_instruccion, entrenador_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (nombre, descripcion, grupo_muscular, tipo, video_instruccion, entrenador_id))
    
    def obtener(self, ejercicio_id: int) -> Dict:
        query = """
        SELECT id, nombre, descripcion, grupo_muscular, tipo, video_instruccion 
        FROM Ejercicio WHERE id = %s
        """
        result = self.execute_query(query, (ejercicio_id,))
        return result[0] if result else None

    def actualizar(self, ejercicio_id: int, set_clause: str, valores: list) -> int:
        query = f"UPDATE Ejercicio SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
    
    def eliminar_relaciones_rutina(self, ejercicio_id: int) -> int:
        return self.execute_update("DELETE FROM Rutina_Ejercicio WHERE id_ejercicio = %s", (ejercicio_id,))
        
    def eliminar(self, ejercicio_id: int) -> int:
        return self.execute_update("DELETE FROM Ejercicio WHERE id = %s", (ejercicio_id,))
    
    def listar_todos(self, limite: int, offset: int) -> List[Dict]:
        query = "SELECT * FROM Ejercicio ORDER BY id LIMIT %s OFFSET %s"
        return self.execute_query(query, (limite, offset))
    
    def listar_por_grupo_muscular(self, grupo_muscular: str) -> List[Dict]:
        query = "SELECT * FROM Ejercicio WHERE grupo_muscular = %s ORDER BY nombre"
        return self.execute_query(query, (grupo_muscular,))
    
    def listar_por_tipo(self, tipo: str) -> List[Dict]:
        query = "SELECT * FROM Ejercicio WHERE tipo = %s ORDER BY nombre"
        return self.execute_query(query, (tipo,))
    
    def buscar(self, termino_busqueda: str, limite: int) -> List[Dict]:
        query = """
        SELECT * FROM Ejercicio 
        WHERE nombre LIKE %s OR descripcion LIKE %s OR grupo_muscular LIKE %s
        ORDER BY nombre 
        LIMIT %s
        """
        return self.execute_query(query, (termino_busqueda, termino_busqueda, termino_busqueda, limite))
    
    def agregar_a_rutina(self, id_rutina: int, id_ejercicio: int, orden: int, series: int, repeticiones: int, duracion: int) -> int:
        query = """
        INSERT INTO Rutina_Ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_update(query, (id_rutina, id_ejercicio, orden, series, repeticiones, duracion))
    
    def obtener_por_entrenador(self, entrenador_id: int, limite: int = 10, offset: int = 0, busqueda: str = "", tipo: str = "todas") -> List[Dict]:
        query = """
        SELECT id, nombre, descripcion, grupo_muscular, tipo, video_instruccion as video_path, entrenador_id
        FROM Ejercicio 
        WHERE (entrenador_id = %s OR entrenador_id IS NULL)
        """
        params = [entrenador_id]
        
        if busqueda:
            query += " AND (nombre LIKE %s OR descripcion LIKE %s OR grupo_muscular LIKE %s)"
            termino = f"%{busqueda}%"
            params.extend([termino, termino, termino])
            
        if tipo and tipo != "todas":
            query += " AND tipo = %s"
            params.append(tipo)
            
        query += """
        ORDER BY id DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limite, offset])
        
        return self.execute_query(query, tuple(params))

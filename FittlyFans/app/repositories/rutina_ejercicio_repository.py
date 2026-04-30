from typing import List, Dict, Tuple
from app.repositories.base_repository import BaseRepository

class RutinaEjercicioRepository(BaseRepository):
    """Repositorio para la gestión de la tabla intermedia Rutina_Ejercicio."""
    
    def agregar_ejercicio(self, id_rutina: int, id_ejercicio: int, orden: int, series: int, repeticiones: int, duracion: int) -> int:
        query = """
        INSERT INTO Rutina_Ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_insert(query, (id_rutina, id_ejercicio, orden, series, repeticiones, duracion))
        
    def actualizar_ejercicio(self, set_clause: str, valores: list) -> int:
        query = f"""
        UPDATE Rutina_Ejercicio 
        SET {set_clause} 
        WHERE id_rutina = %s AND id_ejercicio = %s
        """
        return self.execute_update(query, tuple(valores))
        
    def eliminar_ejercicio(self, id_rutina: int, id_ejercicio: int) -> int:
        query = """
        DELETE FROM Rutina_Ejercicio 
        WHERE id_rutina = %s AND id_ejercicio = %s
        """
        return self.execute_update(query, (id_rutina, id_ejercicio))
        
    def listar_ejercicios_rutina(self, id_rutina: int) -> List[Dict]:
        query = """
        SELECT e.*, re.orden, re.series, re.repeticiones, re.duracion
        FROM Rutina_Ejercicio re
        JOIN Ejercicio e ON re.id_ejercicio = e.id
        WHERE re.id_rutina = %s
        ORDER BY re.orden
        """
        return self.execute_query(query, (id_rutina,))
        
    def reordenar_ejercicios(self, id_rutina: int, nuevo_orden: List[Tuple[int, int]]) -> bool:
        try:
            if not self.db.connect():
                return False
            for id_ejercicio, orden in nuevo_orden:
                query = """
                UPDATE Rutina_Ejercicio 
                SET orden = %s 
                WHERE id_rutina = %s AND id_ejercicio = %s
                """
                self.db.cursor.execute(query, (orden, id_rutina, id_ejercicio))
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"Error al reordenar ejercicios: {e}")
            return False

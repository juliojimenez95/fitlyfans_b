from typing import List, Dict
from app.controllers.base_controller import BaseController


class RutinaEjercicioController(BaseController):
    """Controlador para la relación entre Rutina y Ejercicio."""
    
    def agregar_ejercicio(self, id_rutina: int, id_ejercicio: int, orden: int, 
                         series: int = None, repeticiones: int = None, duracion: int = None) -> bool:
        """
        Agrega un ejercicio a una rutina.
        
        Args:
            id_rutina: ID de la rutina
            id_ejercicio: ID del ejercicio
            orden: Orden del ejercicio en la rutina
            series: Número de series (opcional)
            repeticiones: Número de repeticiones por serie (opcional)
            duracion: Duración en segundos (opcional)
            
        Returns:
            True si la inserción fue exitosa, False en caso contrario
        """
        query = """
        INSERT INTO Rutina_Ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        filas_afectadas = self._execute_update(query, (id_rutina, id_ejercicio, orden, series, repeticiones, duracion))
        return filas_afectadas > 0
    
    def actualizar_ejercicio(self, id_rutina: int, id_ejercicio: int, datos: Dict) -> bool:
        """
        Actualiza los detalles de un ejercicio en una rutina.
        
        Args:
            id_rutina: ID de la rutina
            id_ejercicio: ID del ejercicio
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        campos_permitidos = ["orden", "series", "repeticiones", "duracion"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(id_rutina)
        valores.append(id_ejercicio)
        
        query = f"""
        UPDATE Rutina_Ejercicio 
        SET {set_clause} 
        WHERE id_rutina = %s AND id_ejercicio = %s
        """
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def eliminar_ejercicio(self, id_rutina: int, id_ejercicio: int) -> bool:
        """
        Elimina un ejercicio de una rutina.
        
        Args:
            id_rutina: ID de la rutina
            id_ejercicio: ID del ejercicio
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = """
        DELETE FROM Rutina_Ejercicio 
        WHERE id_rutina = %s AND id_ejercicio = %s
        """
        filas_afectadas = self._execute_update(query, (id_rutina, id_ejercicio))
        return filas_afectadas > 0
    
    def listar_ejercicios_rutina(self, id_rutina: int) -> List[Dict]:
        """
        Lista todos los ejercicios de una rutina con sus detalles.
        
        Args:
            id_rutina: ID de la rutina
            
        Returns:
            Lista de ejercicios de la rutina con sus detalles
        """
        query = """
        SELECT e.*, re.orden, re.series, re.repeticiones, re.duracion
        FROM Rutina_Ejercicio re
        JOIN Ejercicio e ON re.id_ejercicio = e.id
        WHERE re.id_rutina = %s
        ORDER BY re.orden
        """
        return self._execute_query(query, (id_rutina,))
    
    def reordenar_ejercicios(self, id_rutina: int, nuevo_orden: List[Tuple[int, int]]) -> bool:
        """
        Reordena los ejercicios de una rutina.
        
        Args:
            id_rutina: ID de la rutina
            nuevo_orden: Lista de tuplas (id_ejercicio, nuevo_orden)
            
        Returns:
            True si la reordenación fue exitosa, False en caso contrario
        """
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
        except Error as e:
            print(f"Error al reordenar ejercicios: {e}")
            return False

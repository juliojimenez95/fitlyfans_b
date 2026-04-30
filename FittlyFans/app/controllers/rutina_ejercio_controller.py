from typing import List, Dict, Tuple
from app.repositories.rutina_ejercicio_repository import RutinaEjercicioRepository

class RutinaEjercicioController:
    """Controlador para la relación entre Rutina y Ejercicio."""
    
    def __init__(self):
        self.rutina_ejercicio_repo = RutinaEjercicioRepository()
        
    def agregar_ejercicio(self, id_rutina: int, id_ejercicio: int, orden: int, 
                         series: int = None, repeticiones: int = None, duracion: int = None) -> bool:
        """Agrega un ejercicio a una rutina."""
        filas_afectadas = self.rutina_ejercicio_repo.agregar_ejercicio(id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        return filas_afectadas > 0
    
    def actualizar_ejercicio(self, id_rutina: int, id_ejercicio: int, datos: Dict) -> bool:
        """Actualiza los detalles de un ejercicio en una rutina."""
        campos_permitidos = ["orden", "series", "repeticiones", "duracion"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(id_rutina)
        valores.append(id_ejercicio)
        
        filas_afectadas = self.rutina_ejercicio_repo.actualizar_ejercicio(set_clause, valores)
        return filas_afectadas > 0
    
    def eliminar_ejercicio(self, id_rutina: int, id_ejercicio: int) -> bool:
        """Elimina un ejercicio de una rutina."""
        filas_afectadas = self.rutina_ejercicio_repo.eliminar_ejercicio(id_rutina, id_ejercicio)
        return filas_afectadas > 0
    
    def listar_ejercicios_rutina(self, id_rutina: int) -> List[Dict]:
        """Lista todos los ejercicios de una rutina con sus detalles."""
        return self.rutina_ejercicio_repo.listar_ejercicios_rutina(id_rutina)
    
    def reordenar_ejercicios(self, id_rutina: int, nuevo_orden: List[Tuple[int, int]]) -> bool:
        """Reordena los ejercicios de una rutina."""
        return self.rutina_ejercicio_repo.reordenar_ejercicios(id_rutina, nuevo_orden)

    def reemplazar_ejercicios(self, id_rutina: int, ejercicios: List[Dict]) -> bool:
        """Elimina los ejercicios actuales de la rutina e inserta los nuevos."""
        try:
            # 1. Eliminar todos los ejercicios asociados a la rutina
            # Ya que no hay un método para eliminar todos en el repo, podemos iterar o usar uno custom, 
            # pero lo mejor es borrar a nivel repositorio. Por ahora iteraremos los existentes y los borraremos.
            existentes = self.listar_ejercicios_rutina(id_rutina)
            for ej in existentes:
                self.eliminar_ejercicio(id_rutina, ej['id'])
            
            # 2. Insertar los nuevos
            for ej in ejercicios:
                self.agregar_ejercicio(
                    id_rutina, 
                    ej['id_ejercicio'], 
                    ej.get('orden', 1), 
                    ej.get('series', 4), 
                    ej.get('repeticiones', 12), 
                    ej.get('duracion', 0)
                )
            return True
        except Exception as e:
            print(f"Error al reemplazar ejercicios: {e}")
            return False

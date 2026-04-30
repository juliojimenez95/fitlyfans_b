from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository

class ProgresoRepository(BaseRepository):
    """Repositorio para la entidad Historial_Entrenamiento."""

    def registrar_rutina_completada(self, suscriptor_id: int, rutina_id: int, asignacion_plan_id: Optional[int] = None, semana: Optional[int] = None, dia: Optional[int] = None, duracion_segundos: Optional[int] = None) -> int:
        query = """
        INSERT INTO Historial_Entrenamiento (suscriptor_id, rutina_id, asignacion_plan_id, semana, dia, duracion_segundos)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (suscriptor_id, rutina_id, asignacion_plan_id, semana, dia, duracion_segundos)
        return self.execute_insert(query, params)

    def verificar_rutina_plan_completada(self, suscriptor_id: int, asignacion_plan_id: int, semana: int, dia: int) -> bool:
        """Verifica si existe un registro de que el usuario ya completó esa rutina de ese plan."""
        query = """
        SELECT id FROM Historial_Entrenamiento 
        WHERE suscriptor_id = %s AND asignacion_plan_id = %s AND semana = %s AND dia = %s
        """
        result = self.execute_query(query, (suscriptor_id, asignacion_plan_id, semana, dia))
        return len(result) > 0

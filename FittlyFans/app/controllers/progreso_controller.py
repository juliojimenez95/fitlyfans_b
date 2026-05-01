from typing import Optional
from app.repositories.progreso_repository import ProgresoRepository
from app.models.db import DatabaseConnectionSingleton

class ProgresoController:
    """Controlador para la lógica de negocio del progreso y entrenamiento."""

    def __init__(self):
        self.progreso_repo = ProgresoRepository()
        self.db = DatabaseConnectionSingleton()

    def registrar_rutina_completada(self, suscriptor_id: int, rutina_id: int, asignacion_plan_id: Optional[int] = None, semana: Optional[int] = None, dia: Optional[int] = None, duracion_segundos: Optional[int] = None) -> bool:
        # Si es parte de un plan, validamos que no se haya completado ya para no duplicar
        if asignacion_plan_id and semana and dia:
            ya_completada = self.progreso_repo.verificar_rutina_plan_completada(
                suscriptor_id, asignacion_plan_id, semana, dia
            )
            if ya_completada:
                return True # Retorna éxito para no afectar la UI, pero no inserta duplicado

        historial_id = self.progreso_repo.registrar_rutina_completada(
            suscriptor_id=suscriptor_id,
            rutina_id=rutina_id,
            asignacion_plan_id=asignacion_plan_id,
            semana=semana,
            dia=dia,
            duracion_segundos=duracion_segundos
        )
        if historial_id > 0:
            self.db.commit()
            return True
        return False

    def obtener_historial_suscriptor(self, suscriptor_id: int):
        return self.progreso_repo.obtener_historial_suscriptor(suscriptor_id)

from typing import List, Dict, Optional
from datetime import datetime, date
from flask import g
from app.repositories.plan_repository import PlanRepository
from app.repositories.progreso_repository import ProgresoRepository
from app.models.db import DatabaseConnectionSingleton

class PlanController:
    """Controlador para la lógica de negocio de los Planes de Entrenamiento."""

    def __init__(self):
        self.plan_repo = PlanRepository()
        self.progreso_repo = ProgresoRepository()
        self.db = DatabaseConnectionSingleton()

    def crear_plan(self, entrenador_id: int, nombre: str, descripcion: str, objetivo: str, nivel: str, duracion_semanas: int, estado: str = 'borrador') -> int:
        plan_id = self.plan_repo.crear_plan(entrenador_id, nombre, descripcion, objetivo, nivel, duracion_semanas, estado)
        if plan_id > 0:
            self.db.commit()
        return plan_id

    def obtener_plan(self, plan_id: int) -> Optional[Dict]:
        return self.plan_repo.obtener_plan(plan_id)

    def listar_planes_entrenador(self, entrenador_id: int) -> List[Dict]:
        return self.plan_repo.listar_planes_entrenador(entrenador_id)

    def actualizar_plan(self, plan_id: int, nombre: str, descripcion: str, objetivo: str, nivel: str, duracion_semanas: int, estado: str) -> bool:
        filas = self.plan_repo.actualizar_plan(plan_id, nombre, descripcion, objetivo, nivel, duracion_semanas, estado)
        if filas > 0:
            self.db.commit()
            return True
        return False

    def eliminar_plan(self, plan_id: int) -> bool:
        filas = self.plan_repo.eliminar_plan(plan_id)
        if filas > 0:
            self.db.commit()
            return True
        return False

    # ---- RUTINAS EN EL PLAN ----
    def agregar_rutina_a_plan(self, plan_id: int, rutina_id: int, semana: int, dia: int) -> bool:
        filas = self.plan_repo.agregar_rutina_a_plan(plan_id, rutina_id, semana, dia)
        if filas > 0:
            self.db.commit()
            return True
        return False

    def remover_rutina_de_plan(self, plan_id: int, semana: int, dia: int) -> bool:
        filas = self.plan_repo.remover_rutina_de_plan(plan_id, semana, dia)
        if filas > 0:
            self.db.commit()
            return True
        return False

    def listar_rutinas_de_plan(self, plan_id: int) -> List[Dict]:
        return self.plan_repo.listar_rutinas_de_plan(plan_id)

    # ---- ASIGNACIONES ----
    def asignar_plan_suscriptor(self, plan_id: int, suscriptor_id: int, entrenador_id: int, fecha_inicio: str) -> bool:
        # fecha_inicio expected format: YYYY-MM-DD
        asignacion_id = self.plan_repo.asignar_plan_suscriptor(plan_id, suscriptor_id, entrenador_id, fecha_inicio)
        if asignacion_id > 0:
            self.db.commit()
            return True
        return False

    def obtener_entrenamiento_hoy(self, suscriptor_id: int) -> Optional[Dict]:
        """Calcula qué rutina le toca hoy al suscriptor basado en su plan activo."""
        asignacion = self.plan_repo.obtener_plan_activo_suscriptor(suscriptor_id)
        if not asignacion:
            return None

        # Obtener fecha de inicio (puede ser datetime.date o str dependiendo del driver de mysql)
        fecha_inicio = asignacion['fecha_inicio']
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        elif isinstance(fecha_inicio, datetime):
            fecha_inicio = fecha_inicio.date()

        hoy = date.today()
        
        # Si el plan empieza en el futuro, no hay entrenamiento hoy
        if hoy < fecha_inicio:
            return {
                'estado': 'futuro',
                'asignacion': asignacion,
                'dias_faltantes': (fecha_inicio - hoy).days
            }

        # Calcular días transcurridos
        dias_transcurridos = (hoy - fecha_inicio).days
        
        # Calcular semana y día (asumiendo semanas de 7 días, indexando desde 1)
        semana_actual = (dias_transcurridos // 7) + 1
        dia_actual = (dias_transcurridos % 7) + 1

        # Verificar si el plan ya terminó
        if semana_actual > asignacion['duracion_semanas']:
            # TODO: Auto-completar el plan
            return {
                'estado': 'completado',
                'asignacion': asignacion
            }

        rutinas_plan = self.listar_rutinas_de_plan(asignacion['plan_id'])
        rutina_hoy = next((r for r in rutinas_plan if r['semana'] == semana_actual and r['dia'] == dia_actual), None)

        if rutina_hoy:
            rutina_hoy['completado'] = self.progreso_repo.verificar_rutina_plan_completada(
                suscriptor_id=suscriptor_id,
                asignacion_plan_id=asignacion['id'],
                semana=semana_actual,
                dia=dia_actual
            )

        return {
            'estado': 'activo',
            'asignacion': asignacion,
            'progreso': {
                'semana_actual': semana_actual,
                'dia_actual': dia_actual,
                'dias_transcurridos': dias_transcurridos,
                'total_semanas': asignacion['duracion_semanas']
            },
            'rutina_hoy': rutina_hoy # Puede ser None si hay descanso
        }

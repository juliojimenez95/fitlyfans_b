from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository

class PlanRepository(BaseRepository):
    """Repositorio para la entidad Plan_Entrenamiento y sus relaciones."""

    def crear_plan(self, entrenador_id: int, nombre: str, descripcion: str, objetivo: str, nivel: str, duracion_semanas: int, estado: str = 'borrador') -> int:
        query = """
        INSERT INTO Plan_Entrenamiento (entrenador_id, nombre, descripcion, objetivo, nivel, duracion_semanas, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (entrenador_id, nombre, descripcion, objetivo, nivel, duracion_semanas, estado)
        return self.execute_insert(query, params)

    def obtener_plan(self, plan_id: int) -> Optional[Dict]:
        query = "SELECT * FROM Plan_Entrenamiento WHERE id = %s"
        result = self.execute_query(query, (plan_id,))
        return result[0] if result else None

    def listar_planes_entrenador(self, entrenador_id: int) -> List[Dict]:
        query = """
        SELECT p.*, COUNT(pr.id) as total_rutinas
        FROM Plan_Entrenamiento p
        LEFT JOIN Plan_Rutina pr ON p.id = pr.plan_id
        WHERE p.entrenador_id = %s
        GROUP BY p.id
        ORDER BY p.fecha_creacion DESC
        """
        return self.execute_query(query, (entrenador_id,))

    def actualizar_plan(self, plan_id: int, nombre: str, descripcion: str, objetivo: str, nivel: str, duracion_semanas: int, estado: str) -> int:
        query = """
        UPDATE Plan_Entrenamiento 
        SET nombre = %s, descripcion = %s, objetivo = %s, nivel = %s, duracion_semanas = %s, estado = %s
        WHERE id = %s
        """
        return self.execute_update(query, (nombre, descripcion, objetivo, nivel, duracion_semanas, estado, plan_id))

    def eliminar_plan(self, plan_id: int) -> int:
        query = "DELETE FROM Plan_Entrenamiento WHERE id = %s"
        return self.execute_update(query, (plan_id,))

    # ---- GESTIÓN DE RUTINAS EN EL PLAN ----
    def agregar_rutina_a_plan(self, plan_id: int, rutina_id: int, semana: int, dia: int) -> int:
        # Usamos REPLACE o ON DUPLICATE KEY UPDATE para que si el entrenador reasigna una rutina a ese mismo día/semana, lo actualice
        query = """
        INSERT INTO Plan_Rutina (plan_id, rutina_id, semana, dia)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE rutina_id = VALUES(rutina_id)
        """
        return self.execute_insert(query, (plan_id, rutina_id, semana, dia))

    def remover_rutina_de_plan(self, plan_id: int, semana: int, dia: int) -> int:
        query = "DELETE FROM Plan_Rutina WHERE plan_id = %s AND semana = %s AND dia = %s"
        return self.execute_update(query, (plan_id, semana, dia))

    def listar_rutinas_de_plan(self, plan_id: int) -> List[Dict]:
        query = """
        SELECT pr.id as plan_rutina_id, pr.semana, pr.dia, r.*
        FROM Plan_Rutina pr
        JOIN Rutina r ON pr.rutina_id = r.id
        WHERE pr.plan_id = %s
        ORDER BY pr.semana ASC, pr.dia ASC
        """
        return self.execute_query(query, (plan_id,))

    # ---- GESTIÓN DE ASIGNACIONES ----
    def asignar_plan_suscriptor(self, plan_id: int, suscriptor_id: int, entrenador_id: int, fecha_inicio: str) -> int:
        # Si ya tiene un plan activo, se podría requerir pausarlo o cancelarlo. 
        # Aquí asumimos que crear la asignación es el objetivo principal.
        query = """
        INSERT INTO Asignacion_Plan (plan_id, suscriptor_id, entrenador_id, fecha_inicio, estado)
        VALUES (%s, %s, %s, %s, 'activo')
        """
        return self.execute_insert(query, (plan_id, suscriptor_id, entrenador_id, fecha_inicio))

    def obtener_plan_activo_suscriptor(self, suscriptor_id: int) -> Optional[Dict]:
        query = """
        SELECT ap.*, p.nombre, p.descripcion, p.duracion_semanas
        FROM Asignacion_Plan ap
        JOIN Plan_Entrenamiento p ON ap.plan_id = p.id
        WHERE ap.suscriptor_id = %s AND ap.estado = 'activo'
        ORDER BY ap.fecha_asignacion DESC
        LIMIT 1
        """
        result = self.execute_query(query, (suscriptor_id,))
        return result[0] if result else None

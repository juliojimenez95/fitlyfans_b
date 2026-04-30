from typing import List, Dict
from app.repositories.rutina_repository import RutinaRepository
from app.models.db import DatabaseConnectionSingleton

class RutinaController:
    """Controlador para la entidad Rutina."""
    
    def __init__(self):
        self.rutina_repo = RutinaRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, id_entrenador: int, nombre: str, descripcion: str = None, 
             nivel_dificultad: str = 'principiante', duracion_estimada: int = 0) -> int:
        """Crea una nueva rutina."""
        rutina_id = self.rutina_repo.crear(id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada)
        if rutina_id:
            self.db.commit()
        return rutina_id
    
    def obtener(self, rutina_id: int) -> Dict:
        """Obtiene una rutina por su ID."""
        rutina = self.rutina_repo.obtener(rutina_id)
        return rutina if rutina else {}
    
    def actualizar(self, rutina_id: int, datos: Dict) -> bool:
        """Actualiza los datos de una rutina."""
        campos_permitidos = ["nombre", "descripcion", "nivel_dificultad", "duracion_estimada"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(rutina_id)
        
        filas_afectadas = self.rutina_repo.actualizar(rutina_id, set_clause, valores)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def eliminar(self, rutina_id: int) -> bool:
        """Elimina una rutina y sus relaciones con ejercicios."""
        self.rutina_repo.eliminar_relaciones_ejercicios(rutina_id)
        filas_afectadas = self.rutina_repo.eliminar(rutina_id)
        if filas_afectadas > 0 or self.rutina_repo.cursor.rowcount >= 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def listar_por_entrenador(self, entrenador_id: int, limite: int = 10, offset: int = 0, busqueda: str = "", dificultad: str = "todas") -> List[Dict]:
        """Lista todas las rutinas creadas por un entrenador con paginacion y filtros."""
        return self.rutina_repo.listar_por_entrenador(entrenador_id, limite, offset, busqueda, dificultad)
    
    def listar_por_nivel(self, nivel_dificultad: str, limite: int = 100) -> List[Dict]:
        """Lista rutinas por nivel de dificultad."""
        return self.rutina_repo.listar_por_nivel(nivel_dificultad, limite)
    
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        """Busca rutinas por nombre o descripción."""
        termino_busqueda = f"%{termino}%"
        return self.rutina_repo.buscar(termino_busqueda, limite)

    def obtener_con_ejercicios(self, rutina_id: int) -> Dict:
        """Obtiene una rutina con su lista de ejercicios ordenados."""
        rutina = self.rutina_repo.obtener_con_ejercicios(rutina_id)
        return rutina if rutina else {}

    def listar_feed_suscriptor(self, suscriptor_id: int) -> List[Dict]:
        """Lista las rutinas de los entrenadores a los que el suscriptor sigue."""
        return self.rutina_repo.listar_feed_suscriptor(suscriptor_id)

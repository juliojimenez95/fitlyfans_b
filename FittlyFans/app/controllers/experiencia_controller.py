from typing import List, Dict
from app.repositories.experiencia_repository import ExperienciaRepository

class ExperienciaController:
    """Controlador para la entidad Experiencia."""
    
    def __init__(self):
        self.experiencia_repo = ExperienciaRepository()
        
    def crear(self, nombre: str, descripcion: str = None) -> int:
        return self.experiencia_repo.crear(nombre, descripcion)
    
    def obtener(self, experiencia_id: int) -> Dict:
        experiencia = self.experiencia_repo.obtener(experiencia_id)
        return experiencia if experiencia else {}
    
    def actualizar(self, experiencia_id: int, nombre: str = None, descripcion: str = None) -> bool:
        actualizaciones = []
        valores = []
        
        if nombre is not None:
            actualizaciones.append("nombre = %s")
            valores.append(nombre)
        
        if descripcion is not None:
            actualizaciones.append("descripcion = %s")
            valores.append(descripcion)
        
        if not actualizaciones:
            return False
        
        set_clause = ", ".join(actualizaciones)
        valores.append(experiencia_id)
        
        filas_afectadas = self.experiencia_repo.actualizar(experiencia_id, set_clause, valores)
        return filas_afectadas > 0
    
    def eliminar(self, experiencia_id: int) -> bool:
        filas_afectadas = self.experiencia_repo.eliminar(experiencia_id)
        return filas_afectadas > 0
    
    def listar_todas(self) -> List[Dict]:
        return self.experiencia_repo.listar_todas()
    
    def buscar(self, termino: str) -> List[Dict]:
        termino_busqueda = f"%{termino}%"
        return self.experiencia_repo.buscar(termino_busqueda)
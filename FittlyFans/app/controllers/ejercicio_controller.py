from typing import List, Dict
from flask import g
from app.repositories.ejercicio_repository import EjercicioRepository
from app.models.db import DatabaseConnectionSingleton

class EjercicioController:
    """Controlador para la entidad Ejercicio."""
    
    def __init__(self):
        self.ejercicio_repo = EjercicioRepository()
        self.db = DatabaseConnectionSingleton()
    
    def crear(self, nombre: str, descripcion: str = None, grupo_muscular: str = None,
             tipo: str = 'fuerza', video_instruccion: str = None, entrenador_id: int = None) -> int:
        """Crea un nuevo ejercicio delegando al repositorio."""
        res = self.ejercicio_repo.crear(nombre, descripcion, grupo_muscular, tipo, video_instruccion, entrenador_id)
        if res > 0:
            self.db.commit()
        return res
    
    def obtener(self, ejercicio_id: int) -> Dict:
        """Obtiene un ejercicio y formatea la URL del video."""
        ejercicio = self.ejercicio_repo.obtener(ejercicio_id)
        if ejercicio and ejercicio.get('video_instruccion'):
            ejercicio['video_url'] = self.obtener_url_video(ejercicio['video_instruccion'])
        return ejercicio if ejercicio else {}
    
    def actualizar(self, ejercicio_id: int, datos: Dict) -> bool:
        """Filtra datos permitidos y delega la actualización."""
        campos_permitidos = ["nombre", "descripcion", "grupo_muscular", "tipo", "video_instruccion"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
            
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        
        filas_afectadas = self.ejercicio_repo.actualizar(ejercicio_id, set_clause, valores)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def eliminar(self, ejercicio_id: int) -> bool:
        """Elimina relaciones y luego el ejercicio."""
        self.ejercicio_repo.eliminar_relaciones_rutina(ejercicio_id)
        filas_afectadas = self.ejercicio_repo.eliminar(ejercicio_id)
        if filas_afectadas > 0 or self.ejercicio_repo.cursor.rowcount >= 0:
            self.db.commit()
        return filas_afectadas > 0
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        return self.ejercicio_repo.listar_todos(limite, offset)
    
    def listar_por_grupo_muscular(self, grupo_muscular: str) -> List[Dict]:
        return self.ejercicio_repo.listar_por_grupo_muscular(grupo_muscular)
    
    def listar_por_tipo(self, tipo: str) -> List[Dict]:
        return self.ejercicio_repo.listar_por_tipo(tipo)
    
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        termino_busqueda = f"%{termino}%"
        return self.ejercicio_repo.buscar(termino_busqueda, limite)
    
    def agregar_a_rutina(self, id_rutina: int, id_ejercicio: int, orden: int, 
                        series: int = None, repeticiones: int = None, duracion: int = None) -> bool:
        filas_afectadas = self.ejercicio_repo.agregar_a_rutina(id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        if filas_afectadas > 0:
            self.db.commit()
        return filas_afectadas > 0

    def obtener_url_video(self, video_path):
        if not video_path:
            return None
        if hasattr(g, 'flask_app'):
            base_url = g.flask_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
        else:
            base_url = 'http://127.0.0.1:5000'
        return f"{base_url}/api/archivos{video_path}"

    def obtener_url_video_alt(self, video_path, base_url='http://127.0.0.1:5000'):
        if not video_path:
            return None
        return f"{base_url}/api/archivos{video_path}"
        
    def obtener_por_entrenador(self, entrenador_id: int, limite: int = 10, offset: int = 0, busqueda: str = "", tipo: str = "todas") -> List[Dict]:
        return self.ejercicio_repo.obtener_por_entrenador(entrenador_id, limite, offset, busqueda, tipo)

from typing import List, Dict
from app.models.db import DatabaseConnectionSingleton
from app.repositories.entrenador_repository import EntrenadorRepository
from app.repositories.usuario_repository import UsuarioRepository

class EntrenadorController:
    """Controlador para la entidad Entrenador."""
    
    def __init__(self):
        self.entrenador_repo = EntrenadorRepository()
        self.usuario_repo = UsuarioRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, usuario_id: int, especialidad: str = None, certificaciones: str = None) -> bool:
        """
        Crea un nuevo entrenador a partir de un usuario existente garantizando
        atomicidad mediante transacciones de Base de Datos.
        """
        try:
            self.db.start_transaction()
            
            # Paso 1: Crear el registro del entrenador
            filas_afectadas = self.entrenador_repo.crear_entrenador(usuario_id, especialidad, certificaciones)
            
            # Paso 2: Actualizar rol en la tabla Usuario
            if filas_afectadas > 0:
                self.usuario_repo.actualizar_tipo_usuario(usuario_id, 'entrenador')
                
            self.db.commit()
            return filas_afectadas > 0
            
        except Exception as e:
            self.db.rollback()
            print(f"Error transaccional en crear entrenador: {e}")
            raise e
    
    def obtener(self, entrenador_id: int) -> Dict:
        """Obtiene la información de un entrenador y su usuario asociado."""
        resultados = self.entrenador_repo.obtener_entrenador_con_usuario(entrenador_id)
        return resultados if resultados else {}
    
    def actualizar(self, entrenador_id: int, especialidad: str = None, certificaciones: str = None) -> bool:
        """Actualiza los datos de un entrenador."""
        actualizaciones = []
        valores = []
        
        if especialidad is not None:
            actualizaciones.append("especialidad = %s")
            valores.append(especialidad)
        
        if certificaciones is not None:
            actualizaciones.append("certificaciones = %s")
            valores.append(certificaciones)
        
        if not actualizaciones:
            return False
            
        set_clause = ", ".join(actualizaciones)
        
        try:
            self.db.start_transaction()
            filas_afectadas = self.entrenador_repo.actualizar_entrenador(entrenador_id, set_clause, valores)
            self.db.commit()
            return filas_afectadas > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Lista todos los entrenadores."""
        return self.entrenador_repo.listar_todos(limite, offset)
    
    def buscar_por_especialidad(self, especialidad: str, limite: int = 100) -> List[Dict]:
        """Busca entrenadores por especialidad."""
        termino_busqueda = f"%{especialidad}%"
        return self.entrenador_repo.buscar_por_especialidad(termino_busqueda, limite)

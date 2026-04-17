from typing import List, Dict
from app.models.db import DatabaseConnectionSingleton
from app.repositories.suscriptor_repository import SuscriptorRepository
from app.repositories.usuario_repository import UsuarioRepository

class SuscriptorController:
    """Controlador para la entidad Suscriptor."""
    
    def __init__(self):
        self.suscriptor_repo = SuscriptorRepository()
        self.usuario_repo = UsuarioRepository()
        self.db = DatabaseConnectionSingleton()
        
    def crear(self, usuario_id: int, objetivo: str = None, nivel_fitness: str = None) -> bool:
        """
        Crea un nuevo suscriptor a partir de un usuario existente garantizando
        atomicidad mediante transacciones de Base de Datos.
        """
        try:
            self.db.start_transaction()
            
            # Paso 1: Crear el registro del suscriptor
            filas_afectadas = self.suscriptor_repo.crear_suscriptor(usuario_id, objetivo, nivel_fitness)
            
            # Paso 2: Actualizar rol en la tabla Usuario
            if filas_afectadas > 0:
                self.usuario_repo.actualizar_tipo_usuario(usuario_id, 'suscriptor')
                
            self.db.commit()
            return filas_afectadas > 0
            
        except Exception as e:
            self.db.rollback()
            print(f"Error transaccional en crear suscriptor: {e}")
            raise e
    
    def obtener(self, suscriptor_id: int) -> Dict:
        """Obtiene la información de un suscriptor y su usuario asociado."""
        resultados = self.suscriptor_repo.obtener_suscriptor_con_usuario(suscriptor_id)
        return resultados if resultados else {}
    
    def actualizar(self, suscriptor_id: int, objetivo: str = None, nivel_fitness: str = None) -> bool:
        """Actualiza los datos de un suscriptor."""
        actualizaciones = []
        valores = []
        
        if objetivo is not None:
            actualizaciones.append("objetivo = %s")
            valores.append(objetivo)
        
        if nivel_fitness is not None:
            actualizaciones.append("nivel_fitness = %s")
            valores.append(nivel_fitness)
        
        if not actualizaciones:
            return False
            
        set_clause = ", ".join(actualizaciones)
        
        try:
            self.db.start_transaction()
            filas_afectadas = self.suscriptor_repo.actualizar_suscriptor(suscriptor_id, set_clause, valores)
            self.db.commit()
            return filas_afectadas > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Lista todos los suscriptores."""
        return self.suscriptor_repo.listar_todos(limite, offset)
    
    def buscar_por_nivel(self, nivel: str, limite: int = 100) -> List[Dict]:
        """Busca suscriptores por nivel de fitness."""
        return self.suscriptor_repo.buscar_por_nivel(nivel, limite)

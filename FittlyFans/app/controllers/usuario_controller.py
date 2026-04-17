from typing import List, Dict
import bcrypt
from app.models.db import DatabaseConnectionSingleton
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.suscriptor_repository import SuscriptorRepository
from app.repositories.entrenador_repository import EntrenadorRepository

class UsuarioController:
    """Controlador para la entidad Usuario."""

    def __init__(self):
        self.db = DatabaseConnectionSingleton()
        self.usuario_repo = UsuarioRepository()
        self.suscriptor_repo = SuscriptorRepository()
        self.entrenador_repo = EntrenadorRepository()
    
    def crear(self, nombre: str, correo: str, contrasena: str, tipo_usuario: str,
          objetivo: str = None, nivel_fitness: str = None,
          especialidad: str = None, certificaciones: str = None) -> int:
        """
        Crea un nuevo usuario y registra información adicional según su tipo.
        Ejecuta la lógica de negocio completa en una sola transacción garantizada.
        """
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            self.db.start_transaction()
            
            # Paso 1: Crear el usuario auth root
            usuario_id = self.usuario_repo.crear_usuario(nombre, correo, hashed_password, tipo_usuario)
            
            if usuario_id == 0:
                self.db.rollback()
                return 0

            # Paso 2: Según el tipo de usuario inicial, crear la sub-entidad para evitar datos a medias
            if tipo_usuario == 'suscriptor':
                filas_s = self.suscriptor_repo.crear_suscriptor(usuario_id, objetivo, nivel_fitness)
                if filas_s == 0:
                    self.db.rollback()
                    return 0

            elif tipo_usuario == 'entrenador':
                filas_e = self.entrenador_repo.crear_entrenador(usuario_id, especialidad, certificaciones)
                if filas_e == 0:
                    self.db.rollback()
                    return 0

            self.db.commit()
            return usuario_id
            
        except Exception as e:
            self.db.rollback()
            print(f"Error transaccional en crear Registro Completo: {e}")
            raise e

    def obtener_por_id(self, usuario_id: int) -> Dict:
        """Obtiene un usuario por su ID."""
        usuario = self.usuario_repo.obtener_por_id(usuario_id)
        return usuario if usuario else {}
    
    def obtener_por_correo(self, correo: str) -> Dict:
        """Obtiene un usuario por su correo electrónico."""
        usuario = self.usuario_repo.obtener_por_correo(correo)
        return usuario if usuario else {}
    
    def actualizar(self, usuario_id: int, datos: Dict) -> bool:
        """Actualiza los datos de un usuario de forma atómica."""
        campos_permitidos = ["nombre", "correo", "contrasena", "tipo_usuario"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
            
        # Si la contraseña fue mandada a actualizar, cifrarla
        if 'contrasena' in campos_a_actualizar:
            pwd = campos_a_actualizar['contrasena']
            campos_a_actualizar['contrasena'] = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        
        try:
            self.db.start_transaction()
            filas_afectadas = self.usuario_repo.actualizar(usuario_id, set_clause, valores)
            self.db.commit()
            return filas_afectadas > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def eliminar(self, usuario_id: int) -> bool:
        """Elimina un usuario atómicamente."""
        try:
            self.db.start_transaction()
            filas_afectadas = self.usuario_repo.eliminar(usuario_id)
            self.db.commit()
            return filas_afectadas > 0
        except Exception as e:
            self.db.rollback()
            raise e
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """Lista todos los usuarios con paginación."""
        return self.usuario_repo.listar_todos(limite, offset)
    
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        """Busca usuarios por nombre o correo."""
        termino_busqueda = f"%{termino}%"
        return self.usuario_repo.buscar(termino, limite)
    
    def contar(self) -> int:
        """Cuenta el número total de usuarios."""
        return self.usuario_repo.contar()
    
    def verificar_credenciales(self, correo: str, contrasena: str) -> Dict:
        """Verifica las credenciales encriptadas de un usuario."""
        usuario = self.usuario_repo.obtener_por_correo(correo)
        
        if not usuario:
            return {}
        
        contraseña_guardada = usuario['contrasena']
        
        if bcrypt.checkpw(contrasena.encode('utf-8'), contraseña_guardada.encode('utf-8')):
            return usuario
        else:
            return {}
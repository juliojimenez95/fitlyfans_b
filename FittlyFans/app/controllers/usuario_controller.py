from typing import List, Dict
import bcrypt
from app.controllers.base_controller import BaseController
from app.controllers.suscriptor_controller import SuscriptorController
from app.controllers.entrenador_controller import EntrenadorController

class UsuarioController(BaseController):
    """Controlador para la entidad Usuario."""

    def __init__(self):
        super().__init__()
        self.suscriptor_controller = SuscriptorController()
        self.entrenador_controller = EntrenadorController()
    
    def crear(self, nombre: str, correo: str, contrasena: str, tipo_usuario: str,
          objetivo: str = None, nivel_fitness: str = None,
          especialidad: str = None, certificaciones: str = None) -> int:
        """
        Crea un nuevo usuario y registra información adicional según su tipo.
        """
        # Encriptar la contraseña
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        query = """
        INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        usuario_id = self._execute_insert(query, (nombre, correo, hashed_password, tipo_usuario))
        
        if usuario_id == 0:
            return 0

        if tipo_usuario == 'suscriptor':
            creado = self.suscriptor_controller.crear(
                usuario_id=usuario_id,
                objetivo=objetivo,
                nivel_fitness=nivel_fitness
            )
            if not creado:
                return 0

        elif tipo_usuario == 'entrenador':
            creado = self.entrenador_controller.crear(
                usuario_id=usuario_id,
                especialidad=especialidad,
                certificaciones=certificaciones
            )
            if not creado:
                return 0

        return usuario_id

    
    def obtener_por_id(self, usuario_id: int) -> Dict:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id: ID del usuario a buscar
            
        Returns:
            Información del usuario o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Usuario WHERE id = %s"
        resultados = self._execute_query(query, (usuario_id,))
        return resultados[0] if resultados else {}
    
    def obtener_por_correo(self, correo: str) -> Dict:
        """
        Obtiene un usuario por su correo electrónico.
        
        Args:
            correo: Correo electrónico del usuario
            
        Returns:
            Información del usuario o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Usuario WHERE correo = %s"
        resultados = self._execute_query(query, (correo,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, usuario_id: int, datos: Dict) -> bool:
        """
        Actualiza los datos de un usuario.
        
        Args:
            usuario_id: ID del usuario a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        campos_permitidos = ["nombre", "correo", "contrasena", "tipo_usuario"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(usuario_id)
        
        query = f"UPDATE Usuario SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def eliminar(self, usuario_id: int) -> bool:
        """
        Elimina un usuario.
        
        Args:
            usuario_id: ID del usuario a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        query = "DELETE FROM Usuario WHERE id = %s"
        filas_afectadas = self._execute_update(query, (usuario_id,))
        return filas_afectadas > 0
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los usuarios con paginación.
        
        Args:
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de usuarios
        """
        query = "SELECT * FROM Usuario ORDER BY id LIMIT %s OFFSET %s"
        return self._execute_query(query, (limite, offset))
    
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        """
        Busca usuarios por nombre o correo.
        
        Args:
            termino: Término de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de usuarios que coinciden con la búsqueda
        """
        termino_busqueda = f"%{termino}%"
        query = """
        SELECT * FROM Usuario 
        WHERE nombre LIKE %s OR correo LIKE %s 
        ORDER BY id LIMIT %s
        """
        return self._execute_query(query, (termino_busqueda, termino_busqueda, limite))
    
    def contar(self) -> int:
        """
        Cuenta el número total de usuarios.
        
        Returns:
            Número total de usuarios
        """
        query = "SELECT COUNT(*) AS total FROM Usuario"
        resultado = self._execute_query(query)
        return resultado[0]["total"] if resultado else 0
    
    def verificar_credenciales(self, correo: str, contrasena: str) -> Dict:
        """
        Verifica las credenciales de un usuario.
        
        Args:
            correo: Correo electrónico del usuario
            contrasena: Contraseña del usuario
        
        Returns:
            Información del usuario si las credenciales son correctas, diccionario vacío en caso contrario
        """
        # Consultar el usuario por correo
        query = "SELECT * FROM Usuario WHERE correo = %s"
        resultados = self._execute_query(query, (correo,))
        
        if not resultados:
            return {}
        
        usuario = resultados[0]
        contraseña_guardada = usuario['contrasena']
        
        # Verificar que la contraseña ingresada coincida con la encriptada en la base de datos
        if bcrypt.checkpw(contrasena.encode('utf-8'), contraseña_guardada.encode('utf-8')):
            return usuario
        else:
            return {}
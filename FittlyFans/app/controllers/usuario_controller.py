from typing import List, Dict
from app.controllers.base_controller import BaseController

class UsuarioController(BaseController):
    """Controlador para la entidad Usuario."""
    
    def crear(self, nombre: str, correo: str, contrasena: str, tipo_usuario: str) -> int:
        """
        Crea un nuevo usuario.
        
        Args:
            nombre: Nombre del usuario
            correo: Correo electrónico del usuario
            contrasena: Contraseña del usuario
            tipo_usuario: Tipo de usuario (generico, suscriptor, entrenador)
            
        Returns:
            ID del usuario creado o 0 si falla
        """
        query = """
        INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        return self._execute_insert(query, (nombre, correo, contrasena, tipo_usuario))
    
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
        query = "SELECT * FROM Usuario WHERE correo = %s AND contrasena = %s"
        resultados = self._execute_query(query, (correo, contrasena))
        return resultados[0] if resultados else {}
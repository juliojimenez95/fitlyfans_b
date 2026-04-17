from typing import List, Dict, Optional
from app.repositories.base_repository import BaseRepository

class UsuarioRepository(BaseRepository):
    
    def crear_usuario(self, nombre: str, correo: str, hashed_password: str, tipo_usuario: str) -> int:
        query = """
        INSERT INTO Usuario (nombre, correo, contrasena, tipo_usuario)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_insert(query, (nombre, correo, hashed_password, tipo_usuario))
        
    def obtener_por_id(self, usuario_id: int) -> Optional[Dict]:
        query = "SELECT * FROM Usuario WHERE id = %s"
        resultados = self.execute_query(query, (usuario_id,))
        return resultados[0] if resultados else None
        
    def obtener_por_correo(self, correo: str) -> Optional[Dict]:
        query = "SELECT * FROM Usuario WHERE correo = %s"
        resultados = self.execute_query(query, (correo,))
        return resultados[0] if resultados else None
        
    def actualizar_tipo_usuario(self, usuario_id: int, tipo_usuario: str) -> int:
        query = "UPDATE Usuario SET tipo_usuario = %s WHERE id = %s"
        return self.execute_update(query, (tipo_usuario, usuario_id))
        
    def actualizar(self, usuario_id: int, set_clause: str, valores: list) -> int:
        valores.append(usuario_id)
        query = f"UPDATE Usuario SET {set_clause} WHERE id = %s"
        return self.execute_update(query, tuple(valores))
        
    def eliminar(self, usuario_id: int) -> int:
        query = "DELETE FROM Usuario WHERE id = %s"
        return self.execute_update(query, (usuario_id,))
        
    def listar_todos(self, limite: int, offset: int) -> List[Dict]:
        query = "SELECT * FROM Usuario ORDER BY id LIMIT %s OFFSET %s"
        return self.execute_query(query, (limite, offset))
        
    def buscar(self, termino_busqueda: str, limite: int) -> List[Dict]:
        query = """
        SELECT * FROM Usuario 
        WHERE nombre LIKE %s OR correo LIKE %s 
        ORDER BY id LIMIT %s
        """
        return self.execute_query(query, (termino_busqueda, termino_busqueda, limite))
        
    def contar(self) -> int:
        query = "SELECT COUNT(*) AS total FROM Usuario"
        resultado = self.execute_query(query)
        return resultado[0]["total"] if resultado else 0

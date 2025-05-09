from typing import List, Dict
from app.controllers.base_controller import BaseController
from flask import Flask, g

class EjercicioController(BaseController):
    """Controlador para la entidad Ejercicio."""
    
    def crear(self, nombre: str, descripcion: str = None, grupo_muscular: str = None,
             tipo: str = 'fuerza', video_instruccion: str = None) -> int:
        """
        Crea un nuevo ejercicio.
        
        Args:
            nombre: Nombre del ejercicio
            descripcion: Descripción del ejercicio (opcional)
            grupo_muscular: Grupo muscular principal (opcional)
            tipo: Tipo de ejercicio (cardio, fuerza, flexibilidad, equilibrio)
            video_instruccion: URL de video instructivo (opcional)
            
        Returns:
            ID del ejercicio creado o 0 si falla
        """
        query = """
        INSERT INTO Ejercicio (nombre, descripcion, grupo_muscular, tipo, video_instruccion)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self._execute_insert(query, (nombre, descripcion, grupo_muscular, tipo, video_instruccion))
    
    def obtener(self, ejercicio_id: int) -> Dict:
        """
        Obtiene un ejercicio por su ID.
        
        Args:
            ejercicio_id: ID del ejercicio
            
        Returns:
            Información del ejercicio o diccionario vacío si no se encuentra
        """
        query = "SELECT * FROM Ejercicio WHERE id = %s"
        resultados = self._execute_query(query, (ejercicio_id,))
        return resultados[0] if resultados else {}
    
    def actualizar(self, ejercicio_id: int, datos: Dict) -> bool:
        """
        Actualiza los datos de un ejercicio.
        
        Args:
            ejercicio_id: ID del ejercicio a actualizar
            datos: Diccionario con los campos a actualizar
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario
        """
        campos_permitidos = ["nombre", "descripcion", "grupo_muscular", "tipo", "video_instruccion"]
        campos_a_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}
        
        if not campos_a_actualizar:
            return False
        
        set_clause = ", ".join([f"{campo} = %s" for campo in campos_a_actualizar.keys()])
        valores = list(campos_a_actualizar.values())
        valores.append(ejercicio_id)
        
        query = f"UPDATE Ejercicio SET {set_clause} WHERE id = %s"
        filas_afectadas = self._execute_update(query, tuple(valores))
        
        return filas_afectadas > 0
    
    def eliminar(self, ejercicio_id: int) -> bool:
        """
        Elimina un ejercicio.
        
        Args:
            ejercicio_id: ID del ejercicio a eliminar
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario
        """
        # Primero eliminar las relaciones en Rutina_Ejercicio
        self._execute_update("DELETE FROM Rutina_Ejercicio WHERE id_ejercicio = %s", (ejercicio_id,))
        
        # Luego eliminar el ejercicio
        query = "DELETE FROM Ejercicio WHERE id = %s"
        filas_afectadas = self._execute_update(query, (ejercicio_id,))
        return filas_afectadas > 0
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista todos los ejercicios con paginación.
        
        Args:
            limite: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de ejercicios
        """
        query = "SELECT * FROM Ejercicio ORDER BY id LIMIT %s OFFSET %s"
        return self._execute_query(query, (limite, offset))
    
    def listar_por_grupo_muscular(self, grupo_muscular: str) -> List[Dict]:
        """
        Lista ejercicios por grupo muscular.
        
        Args:
            grupo_muscular: Grupo muscular a buscar
            
        Returns:
            Lista de ejercicios del grupo muscular especificado
        """
        query = "SELECT * FROM Ejercicio WHERE grupo_muscular = %s ORDER BY nombre"
        return self._execute_query(query, (grupo_muscular,))
    
    def listar_por_tipo(self, tipo: str) -> List[Dict]:
        """
        Lista ejercicios por tipo.
        
        Args:
            tipo: Tipo de ejercicio a buscar
            
        Returns:
            Lista de ejercicios del tipo especificado
        """
        query = "SELECT * FROM Ejercicio WHERE tipo = %s ORDER BY nombre"
        return self._execute_query(query, (tipo,))
    
    # Completando el método buscar() del EjercicioController que quedó incompleto
    def buscar(self, termino: str, limite: int = 100) -> List[Dict]:
        """
        Busca ejercicios por nombre o descripción.
        
        Args:
            termino: Término de búsqueda
            limite: Número máximo de resultados
            
        Returns:
            Lista de ejercicios que coinciden con la búsqueda
        """
        termino_busqueda = f"%{termino}%"
        query = """
        SELECT * FROM Ejercicio 
        WHERE nombre LIKE %s OR descripcion LIKE %s OR grupo_muscular LIKE %s
        ORDER BY nombre 
        LIMIT %s
        """
        return self._execute_query(query, (termino_busqueda, termino_busqueda, termino_busqueda, limite))
    
    def agregar_a_rutina(self, id_rutina: int, id_ejercicio: int, orden: int, 
                        series: int = None, repeticiones: int = None, duracion: int = None) -> bool:
        """
        Añade un ejercicio a una rutina.
        
        Args:
            id_rutina: ID de la rutina
            id_ejercicio: ID del ejercicio a añadir
            orden: Orden del ejercicio en la rutina
            series: Número de series (opcional)
            repeticiones: Número de repeticiones por serie (opcional)
            duracion: Duración en segundos (opcional)
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        query = """
        INSERT INTO Rutina_Ejercicio (id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        filas_afectadas = self._execute_update(query, (id_rutina, id_ejercicio, orden, series, repeticiones, duracion))
        return filas_afectadas > 0
    

    def obtener_url_video(self, video_path):
        """
        Convierte una ruta relativa de video a una URL completa
        
        Args:
            video_path: Ruta relativa del video
            
        Returns:
            URL completa del video
        """
        if not video_path:
            return None
        
        # Usando g.flask_app si lo tienes configurado
        # (deberías almacenar la instancia de la app en g.flask_app durante la inicialización)
        if hasattr(g, 'flask_app'):
            base_url = g.flask_app.config.get('BASE_URL', 'http://127.0.0.1:5000')
        else:
            # O simplemente usar una URL base hardcodeada si no tienes acceso a la config
            base_url = 'http://127.0.0.1:5000'
            
        return f"{base_url}/api/ejercicios{video_path}"

    # Alternativa: Pasar la base_url como argumento
    def obtener_url_video_alt(self, video_path, base_url='http://127.0.0.1:5000'):
        """
        Convierte una ruta relativa de video a una URL completa
        
        Args:
            video_path: Ruta relativa del video
            base_url: URL base del servidor
            
        Returns:
            URL completa del video
        """
        if not video_path:
            return None
            
        return f"{base_url}/api/ejercicios{video_path}"

    # Modificar el método para obtener un ejercicio para que devuelva la URL completa del video
    def obtener(self, ejercicio_id: int):
        """
        Obtiene un ejercicio por su ID
        
        Args:
            ejercicio_id: ID del ejercicio a buscar
            
        Returns:
            Diccionario con la información del ejercicio o None si no existe
        """
        query = """
        SELECT id, nombre, descripcion, grupo_muscular, tipo, video_instruccion
        FROM Ejercicio WHERE id = %s
        """
        result = self._execute_query(query, (ejercicio_id,))
        
        if result and len(result) > 0:
            ejercicio = result[0]
            # Generar URL completa para el video si existe
            if ejercicio['video_instruccion']:
                ejercicio['video_url'] = self.obtener_url_video(ejercicio['video_instruccion'])
            return ejercicio
        return None

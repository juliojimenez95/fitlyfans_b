from flasgger import swag_from
from flask import Blueprint, request, jsonify,send_from_directory
from app.controllers.ejercicio_controller import EjercicioController
from app.utils.auth import token_required
import os
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
import uuid

ejercicio_bp = Blueprint('ejercicio', __name__)
ejercicio_controller = EjercicioController()

# Agregar esta función para manejar la subida de archivos
def allowed_video_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm', '3gp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Añadir esta configuración en el archivo de inicialización de Flask (app.py o __init__.py)
# app.config['UPLOAD_FOLDER'] = 'uploads/videos'
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

# Asegúrate de crear el directorio de subidas
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# Modificación de la ruta para manejar la subida de archivos
@ejercicio_bp.route('', methods=['POST'])
@token_required
@swag_from('../../docs_api/ejercicio/crear_ejercicio.yml')
def crear_ejercicio(*args, **kwargs):
    try:
        # Obtener el usuario autenticado desde el decorador
        entrenador = kwargs.get('current_user')
        entrenador_id = entrenador.get('id') if entrenador else None

        print('Usuario autenticado:', entrenador)

        if not entrenador_id:
            return jsonify({'error': 'No se pudo identificar al entrenador'}), 403

        # (Opcional) Validar que el rol sea "entrenador"
        if entrenador.get('rol') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        # Asegúrate de que existe el directorio para subir
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'videos')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Extraer datos del formulario
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        grupo_muscular = request.form.get('grupo_muscular')
        tipo = request.form.get('tipo', 'fuerza')

        if not nombre:
            return jsonify({'error': 'El nombre es obligatorio'}), 400

        # Manejar la subida de video
        video_path = None
        if 'video' in request.files:
            video_file = request.files['video']
            if video_file.filename != '':
                if allowed_video_file(video_file.filename):
                    filename = secure_filename(video_file.filename)
                    filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(upload_folder, filename)
                    video_file.save(file_path)
                    video_path = f"/uploads/videos/{filename}"
                else:
                    return jsonify({'error': 'Tipo de archivo no permitido. Use mp4, mov, avi, webm o 3gp'}), 400

        # Crear el ejercicio en la base de datos
        ejercicio_id = ejercicio_controller.crear(
            nombre, descripcion, grupo_muscular, tipo, video_path, entrenador_id
        )

        return jsonify({
            'mensaje': 'Ejercicio creado',
            'id_ejercicio': ejercicio_id,
            'video_path': video_path
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error al crear ejercicio: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

# Añadir una ruta para servir los videos
@ejercicio_bp.route('/videos/<path:filename>')
@swag_from('../../docs_api/ejercicio/serve_video.yml')
def serve_video(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads', 'videos'), filename)

# Obtener ejercicio por ID
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/obtener_ejercicio.yml')
def obtener_ejercicio(ejercicio_id, *args, **kwargs):
    ejercicio = ejercicio_controller.obtener(ejercicio_id)
    if not ejercicio:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404
    return jsonify(ejercicio), 200

# Actualizar ejercicio
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['PUT'])
@token_required
@swag_from('../../docs_api/ejercicio/actualizar_ejercicio.yml')
def actualizar_ejercicio(ejercicio_id, *args, **kwargs):
    datos = request.json
    actualizado = ejercicio_controller.actualizar(ejercicio_id, datos)
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar el ejercicio'}), 400
    return jsonify({'mensaje': 'Ejercicio actualizado correctamente'}), 200

# Eliminar ejercicio
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['DELETE'])
@token_required
@swag_from('../../docs_api/ejercicio/eliminar_ejercicio.yml')
def eliminar_ejercicio(ejercicio_id, *args, **kwargs):
    eliminado = ejercicio_controller.eliminar(ejercicio_id)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el ejercicio'}), 400
    return jsonify({'mensaje': 'Ejercicio eliminado correctamente'}), 200

# Listar todos los ejercicios con paginación
@ejercicio_bp.route('', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/listar_ejercicios.yml')
def listar_ejercicios(*args, **kwargs):
    limite = int(request.args.get('limite', 100))
    offset = int(request.args.get('offset', 0))
    ejercicios = ejercicio_controller.listar_todos(limite, offset)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Buscar ejercicios
@ejercicio_bp.route('/buscar', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/buscar_ejercicios.yml')
def buscar_ejercicios(*args, **kwargs):
    termino = request.args.get('termino', '')
    limite = int(request.args.get('limite', 100))
    resultados = ejercicio_controller.buscar(termino, limite)
    return jsonify({'total': len(resultados), 'resultados': resultados}), 200

# Listar ejercicios por grupo muscular
@ejercicio_bp.route('/grupo/<string:grupo_muscular>', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/listar_por_grupo_muscular.yml')
def listar_por_grupo_muscular(grupo_muscular, *args, **kwargs):
    ejercicios = ejercicio_controller.listar_por_grupo_muscular(grupo_muscular)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Listar ejercicios por tipo
@ejercicio_bp.route('/tipo/<string:tipo>', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/listar_por_tipo.yml')
def listar_por_tipo(tipo, *args, **kwargs):
    ejercicios = ejercicio_controller.listar_por_tipo(tipo)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Agregar ejercicio a una rutina
@ejercicio_bp.route('/rutina', methods=['POST'])
@token_required
@swag_from('../../docs_api/ejercicio/agregar_a_rutina.yml')
def agregar_a_rutina(*args, **kwargs):
    data = request.json
    id_rutina = data.get('id_rutina')
    id_ejercicio = data.get('id_ejercicio')
    orden = data.get('orden')
    series = data.get('series')
    repeticiones = data.get('repeticiones')
    duracion = data.get('duracion')

    if not all([id_rutina, id_ejercicio, orden]):
        return jsonify({'error': 'id_rutina, id_ejercicio y orden son obligatorios'}), 400

    agregado = ejercicio_controller.agregar_a_rutina(id_rutina, id_ejercicio, orden, series, repeticiones, duracion)
    if not agregado:
        return jsonify({'error': 'No se pudo agregar el ejercicio a la rutina'}), 400
    return jsonify({'mensaje': 'Ejercicio agregado a la rutina'}), 201

# Ruta para obtener los ejercicios del entrenador autenticado
@ejercicio_bp.route('', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/obtener_ejercicios_entrenador.yml')
def obtener_ejercicios_entrenador(*args, **kwargs):
    try:
        # Obtener el usuario autenticado desde el decorador
        entrenador = kwargs.get('current_user')
        entrenador_id = entrenador.get('id') if entrenador else None

        print('Usuario autenticado:', entrenador)

        if not entrenador_id:
            return jsonify({'error': 'No se pudo identificar al entrenador'}), 403

        # (Opcional) Validar que el rol sea "entrenador"
        if entrenador.get('rol') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        # Obtener los ejercicios del entrenador desde el controlador
        ejercicios = ejercicio_controller.obtener_por_entrenador(entrenador_id)

        # Si no hay ejercicios, devolver lista vacía
        if not ejercicios:
            return jsonify({
                'mensaje': 'No se encontraron ejercicios para este entrenador',
                'ejercicios': []
            }), 200

        return jsonify({
            'mensaje': 'Ejercicios obtenidos correctamente',
            'ejercicios': ejercicios,
            'total': len(ejercicios)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error al obtener ejercicios del entrenador: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500


# Ruta alternativa para obtener ejercicios de un entrenador específico por ID
# (útil si necesitas obtener ejercicios de otro entrenador, solo para admin)
@ejercicio_bp.route('/entrenador/<int:entrenador_id>', methods=['GET'])
@token_required
@swag_from('../../docs_api/ejercicio/obtener_ejercicios_por_entrenador_id.yml')
def obtener_ejercicios_por_entrenador_id(entrenador_id, *args, **kwargs):
    try:
        # Obtener el usuario autenticado desde el decorador
        usuario_actual = kwargs.get('current_user')
        
        if not usuario_actual:
            return jsonify({'error': 'No se pudo identificar al usuario'}), 403

        # Solo permitir si es el mismo entrenador o si es admin
        if usuario_actual.get('id') != entrenador_id and usuario_actual.get('rol') != 'admin':
            return jsonify({'error': 'No autorizado. Solo puedes ver tus propios ejercicios'}), 403

        # Obtener los ejercicios del entrenador específico
        ejercicios = ejercicio_controller.obtener_por_entrenador(entrenador_id)

        if not ejercicios:
            return jsonify({
                'mensaje': 'No se encontraron ejercicios para este entrenador',
                'ejercicios': []
            }), 200

        return jsonify({
            'mensaje': 'Ejercicios obtenidos correctamente',
            'ejercicios': ejercicios,
            'total': len(ejercicios)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error al obtener ejercicios del entrenador {entrenador_id}: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

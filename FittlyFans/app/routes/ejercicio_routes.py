from flask import Blueprint, request, jsonify
from app.controllers.ejercicio_controller import EjercicioController
from app.utils.auth import token_required

ejercicio_bp = Blueprint('ejercicio', __name__)
ejercicio_controller = EjercicioController()

# Crear un nuevo ejercicio
@ejercicio_bp.route('', methods=['POST'])
@token_required
def crear_ejercicio(*args, **kwargs):
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    grupo_muscular = data.get('grupo_muscular')
    tipo = data.get('tipo', 'fuerza')
    video_instruccion = data.get('video_instruccion')

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    ejercicio_id = ejercicio_controller.crear(nombre, descripcion, grupo_muscular, tipo, video_instruccion)
    return jsonify({'mensaje': 'Ejercicio creado', 'id_ejercicio': ejercicio_id}), 201

# Obtener ejercicio por ID
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['GET'])
@token_required
def obtener_ejercicio(ejercicio_id, *args, **kwargs):
    ejercicio = ejercicio_controller.obtener(ejercicio_id)
    if not ejercicio:
        return jsonify({'error': 'Ejercicio no encontrado'}), 404
    return jsonify(ejercicio), 200

# Actualizar ejercicio
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['PUT'])
@token_required
def actualizar_ejercicio(ejercicio_id, *args, **kwargs):
    datos = request.json
    actualizado = ejercicio_controller.actualizar(ejercicio_id, datos)
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar el ejercicio'}), 400
    return jsonify({'mensaje': 'Ejercicio actualizado correctamente'}), 200

# Eliminar ejercicio
@ejercicio_bp.route('/<int:ejercicio_id>', methods=['DELETE'])
@token_required
def eliminar_ejercicio(ejercicio_id, *args, **kwargs):
    eliminado = ejercicio_controller.eliminar(ejercicio_id)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar el ejercicio'}), 400
    return jsonify({'mensaje': 'Ejercicio eliminado correctamente'}), 200

# Listar todos los ejercicios con paginación
@ejercicio_bp.route('', methods=['GET'])
@token_required
def listar_ejercicios(*args, **kwargs):
    limite = int(request.args.get('limite', 100))
    offset = int(request.args.get('offset', 0))
    ejercicios = ejercicio_controller.listar_todos(limite, offset)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Buscar ejercicios
@ejercicio_bp.route('/buscar', methods=['GET'])
@token_required
def buscar_ejercicios(*args, **kwargs):
    termino = request.args.get('termino', '')
    limite = int(request.args.get('limite', 100))
    resultados = ejercicio_controller.buscar(termino, limite)
    return jsonify({'total': len(resultados), 'resultados': resultados}), 200

# Listar ejercicios por grupo muscular
@ejercicio_bp.route('/grupo/<string:grupo_muscular>', methods=['GET'])
@token_required
def listar_por_grupo_muscular(grupo_muscular, *args, **kwargs):
    ejercicios = ejercicio_controller.listar_por_grupo_muscular(grupo_muscular)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Listar ejercicios por tipo
@ejercicio_bp.route('/tipo/<string:tipo>', methods=['GET'])
@token_required
def listar_por_tipo(tipo, *args, **kwargs):
    ejercicios = ejercicio_controller.listar_por_tipo(tipo)
    return jsonify({'total': len(ejercicios), 'ejercicios': ejercicios}), 200

# Agregar ejercicio a una rutina
@ejercicio_bp.route('/rutina', methods=['POST'])
@token_required
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

from flask import Blueprint, request, jsonify
from app.controllers.experiencia_controller import ExperienciaController
from app.utils.auth import token_required

experiencia_bp = Blueprint('experiencia', __name__)
experiencia_controller = ExperienciaController()

# Crear una nueva experiencia
@experiencia_bp.route('', methods=['POST'])
@token_required
def crear_experiencia(*args, **kwargs):
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')

    if not nombre:
        return jsonify({'error': 'El nombre es obligatorio'}), 400

    id_experiencia = experiencia_controller.crear(nombre, descripcion)
    return jsonify({'mensaje': 'Experiencia creada', 'id_experiencia': id_experiencia}), 201

# Obtener experiencia por ID
@experiencia_bp.route('/<int:id_experiencia>', methods=['GET'])
@token_required
def obtener_experiencia(id_experiencia, *args, **kwargs):
    experiencia = experiencia_controller.obtener(id_experiencia)
    if not experiencia:
        return jsonify({'error': 'Experiencia no encontrada'}), 404
    return jsonify(experiencia), 200

# Actualizar experiencia
@experiencia_bp.route('/<int:id_experiencia>', methods=['PUT'])
@token_required
def actualizar_experiencia(id_experiencia, *args, **kwargs):
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')

    actualizado = experiencia_controller.actualizar(id_experiencia, nombre, descripcion)
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar la experiencia'}), 400

    return jsonify({'mensaje': 'Experiencia actualizada correctamente'}), 200

# Eliminar experiencia
@experiencia_bp.route('/<int:id_experiencia>', methods=['DELETE'])
@token_required
def eliminar_experiencia(id_experiencia, *args, **kwargs):
    eliminado = experiencia_controller.eliminar(id_experiencia)
    if not eliminado:
        return jsonify({'error': 'No se pudo eliminar la experiencia'}), 400
    return jsonify({'mensaje': 'Experiencia eliminada correctamente'}), 200

# Listar todas las experiencias
@experiencia_bp.route('', methods=['GET'])
@token_required
def listar_experiencias(*args, **kwargs):
    experiencias = experiencia_controller.listar_todas()
    return jsonify({'total': len(experiencias), 'experiencias': experiencias}), 200

# Buscar experiencias
@experiencia_bp.route('/buscar', methods=['GET'])
@token_required
def buscar_experiencias(*args, **kwargs):
    termino = request.args.get('termino', '')
    resultados = experiencia_controller.buscar(termino)
    return jsonify({'total': len(resultados), 'resultados': resultados}), 200

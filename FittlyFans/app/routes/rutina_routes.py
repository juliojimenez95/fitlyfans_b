from flasgger import swag_from
from flask import Blueprint, request, jsonify
from app.controllers.rutina_controller import RutinaController
from app.utils.auth import token_required

rutina_bp = Blueprint("rutina", __name__)
rutina_controller = RutinaController()

@rutina_bp.route("/rutinas", methods=["POST"])
# @token_required
@swag_from('../../docs_api/rutina/crear_rutina.yml')
def crear_rutina(*args, **kwargs):
    data = request.get_json()

    id_entrenador = data.get("id_entrenador")
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    nivel_dificultad = data.get("nivel_dificultad", "principiante")
    duracion_estimada = data.get("duracion_estimada", 0)

    rutina_id = rutina_controller.crear(id_entrenador, nombre, descripcion, nivel_dificultad, duracion_estimada)
    
    if rutina_id:
        return jsonify({"id": rutina_id}), 201
    else:
        return jsonify({"error": "No se pudo crear la rutina"}), 400

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/obtener_rutina.yml')
def obtener_rutina(rutina_id):
    rutina = rutina_controller.obtener(rutina_id)
    return jsonify(rutina), 200 if rutina else 404

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["PUT"])
@token_required
@swag_from('../../docs_api/rutina/actualizar_rutina.yml')
def actualizar_rutina(rutina_id):
    datos = request.get_json()
    exito = rutina_controller.actualizar(rutina_id, datos)
    return jsonify({"actualizado": exito}), 200 if exito else 400

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["DELETE"])
@token_required
@swag_from('../../docs_api/rutina/eliminar_rutina.yml')
def eliminar_rutina(rutina_id):
    exito = rutina_controller.eliminar(rutina_id)
    return jsonify({"eliminado": exito}), 200 if exito else 400

@rutina_bp.route("/rutinas/entrenador/<int:entrenador_id>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/listar_por_entrenador.yml')
def listar_por_entrenador(entrenador_id):
    rutinas = rutina_controller.listar_por_entrenador(entrenador_id)
    return jsonify(rutinas), 200

@rutina_bp.route("/rutinas/nivel/<string:nivel>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/listar_por_nivel.yml')
def listar_por_nivel(nivel):
    limite = int(request.args.get("limite", 100))
    rutinas = rutina_controller.listar_por_nivel(nivel, limite)
    return jsonify(rutinas), 200

@rutina_bp.route("/rutinas/buscar", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/buscar_rutinas.yml')
def buscar_rutinas():
    termino = request.args.get("termino", "")
    limite = int(request.args.get("limite", 100))
    resultados = rutina_controller.buscar(termino, limite)
    return jsonify(resultados), 200

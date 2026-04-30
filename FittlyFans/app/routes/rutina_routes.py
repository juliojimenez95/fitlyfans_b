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

@rutina_bp.route("/rutinas/feed", methods=["GET"])
@token_required
def feed_suscriptor(current_user=None, **kwargs):
    if isinstance(current_user, dict):
        id_suscriptor = current_user.get('id')
    else:
        id_suscriptor = current_user[0] if isinstance(current_user, tuple) else getattr(current_user, 'id', None)
        
    rutinas = rutina_controller.listar_feed_suscriptor(id_suscriptor)
    return jsonify(rutinas), 200

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/obtener_rutina.yml')
def obtener_rutina(rutina_id, **kwargs):
    rutina = rutina_controller.obtener_con_ejercicios(rutina_id)
    return jsonify(rutina), 200 if rutina else 404

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["PUT"])
@token_required
@swag_from('../../docs_api/rutina/actualizar_rutina.yml')
def actualizar_rutina(rutina_id, *args, **kwargs):
    datos = request.get_json()
    exito = rutina_controller.actualizar(rutina_id, datos)
    return jsonify({"actualizado": exito}), 200 if exito else 400

@rutina_bp.route("/rutinas/<int:rutina_id>", methods=["DELETE"])
@token_required
@swag_from('../../docs_api/rutina/eliminar_rutina.yml')
def eliminar_rutina(rutina_id, *args, **kwargs):
    exito = rutina_controller.eliminar(rutina_id)
    return jsonify({"eliminado": exito}), 200 if exito else 400

from app.controllers.rutina_ejercio_controller import RutinaEjercicioController

@rutina_bp.route("/rutinas/<int:rutina_id>/ejercicios", methods=["PUT"])
@token_required
def reemplazar_ejercicios(rutina_id, *args, **kwargs):
    datos = request.get_json()
    ejercicios = datos.get('ejercicios', [])
    
    rutina_ej_controller = RutinaEjercicioController()
    exito = rutina_ej_controller.reemplazar_ejercicios(rutina_id, ejercicios)
    
    return jsonify({"actualizado": exito}), 200 if exito else 400

@rutina_bp.route("/rutinas/entrenador/<int:entrenador_id>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/listar_por_entrenador.yml')
def listar_por_entrenador(entrenador_id, *args, **kwargs):
    limite = int(request.args.get('limit', 10))
    pagina = int(request.args.get('page', 1))
    busqueda = request.args.get('search', '')
    dificultad = request.args.get('nivel', 'todas')
    
    offset = (pagina - 1) * limite
    rutinas = rutina_controller.listar_por_entrenador(entrenador_id, limite, offset, busqueda, dificultad)
    return jsonify(rutinas), 200

@rutina_bp.route("/rutinas/nivel/<string:nivel>", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/listar_por_nivel.yml')
def listar_por_nivel(nivel, *args, **kwargs):
    limite = int(request.args.get("limite", 100))
    rutinas = rutina_controller.listar_por_nivel(nivel, limite)
    return jsonify(rutinas), 200

@rutina_bp.route("/rutinas/buscar", methods=["GET"])
@token_required
@swag_from('../../docs_api/rutina/buscar_rutinas.yml')
def buscar_rutinas(*args, **kwargs):
    termino = request.args.get("termino", "")
    limite = int(request.args.get("limite", 100))
    resultados = rutina_controller.buscar(termino, limite)
    return jsonify(resultados), 200

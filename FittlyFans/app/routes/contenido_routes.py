from flask import Blueprint, request, jsonify
from app.controllers.contenido_controller import ContenidoController
from app.utils.auth import token_required

contenido_bp = Blueprint("contenido", __name__)
contenido_controller = ContenidoController()

@contenido_bp.route("/contenidos", methods=["POST"])
@token_required
def crear_contenido():
    data = request.get_json()
    id_usuario = data.get("id_usuario")
    descripcion = data.get("descripcion")
    tipo = data.get("tipo")

    contenido_id = contenido_controller.crear(id_usuario, descripcion, tipo)
    return jsonify({"id": contenido_id}), 201 if contenido_id else 400

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["GET"])
@token_required
def obtener_contenido(contenido_id):
    contenido = contenido_controller.obtener(contenido_id)
    return jsonify(contenido), 200 if contenido else 404

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["PUT"])
@token_required
def actualizar_contenido(contenido_id):
    data = request.get_json()
    descripcion = data.get("descripcion")
    exito = contenido_controller.actualizar(contenido_id, descripcion)
    return jsonify({"actualizado": exito}), 200 if exito else 400

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["DELETE"])
@token_required
def eliminar_contenido(contenido_id):
    exito = contenido_controller.eliminar(contenido_id)
    return jsonify({"eliminado": exito}), 200 if exito else 400

@contenido_bp.route("/contenidos/usuario/<int:id_usuario>", methods=["GET"])
@token_required
def listar_contenidos_por_usuario(id_usuario):
    limite = int(request.args.get("limite", 50))
    offset = int(request.args.get("offset", 0))
    contenidos = contenido_controller.listar_por_usuario(id_usuario, limite, offset)
    return jsonify(contenidos), 200

@contenido_bp.route("/contenidos/tipo/<string:tipo>", methods=["GET"])
@token_required
def listar_contenidos_por_tipo(tipo):
    limite = int(request.args.get("limite", 50))
    contenidos = contenido_controller.listar_por_tipo(tipo, limite)
    return jsonify(contenidos), 200

@contenido_bp.route("/contenidos/buscar", methods=["GET"])
@token_required
def buscar_contenidos():
    termino = request.args.get("termino", "")
    limite = int(request.args.get("limite", 50))
    resultados = contenido_controller.buscar(termino, limite)
    return jsonify(resultados), 200

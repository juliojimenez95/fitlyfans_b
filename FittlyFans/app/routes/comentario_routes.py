from flask import Blueprint, request, jsonify
from app.controllers.comentario_controller import ComentarioController
from app.utils.auth import token_required

comentario_bp = Blueprint("comentario", __name__)
comentario_controller = ComentarioController()

@comentario_bp.route('', methods=['POST'])
@token_required
def crear_comentario(*args, **kwargs):
    data = request.get_json()
    id_usuario = data.get("id_usuario")
    id_contenido = data.get("id_contenido")
    descripcion = data.get("descripcion")

    comentario_id = comentario_controller.crear(id_usuario, id_contenido, descripcion)
    return jsonify({"id": comentario_id}), 201 if comentario_id else 400

@comentario_bp.route('/<int:comentario_id>', methods=['GET'])
@token_required
def obtener_comentario(comentario_id, *args, **kwargs):
    comentario = comentario_controller.obtener(comentario_id)
    return jsonify(comentario), 200 if comentario else 404

@comentario_bp.route('/<int:comentario_id>', methods=['PUT'])
@token_required
def actualizar_comentario(comentario_id, *args, **kwargs):
    data = request.get_json()
    descripcion = data.get("descripcion")
    exito = comentario_controller.actualizar(comentario_id, descripcion)
    return jsonify({"actualizado": exito}), 200 if exito else 400

@comentario_bp.route('/<int:comentario_id>', methods=['DELETE'])
@token_required
def eliminar_comentario(comentario_id, *args, **kwargs):
    exito = comentario_controller.eliminar(comentario_id)
    return jsonify({"eliminado": exito}), 200 if exito else 400

@comentario_bp.route('/contenido/<int:id_contenido>', methods=['GET'])
@token_required
def listar_comentarios_por_contenido(id_contenido, *args, **kwargs):
    comentarios = comentario_controller.listar_por_contenido(id_contenido)
    return jsonify(comentarios), 200

@comentario_bp.route('/usuario/<int:id_usuario>', methods=['GET'])
@token_required
def listar_comentarios_por_usuario(id_usuario, *args, **kwargs):
    limite = int(request.args.get("limite", 50))
    comentarios = comentario_controller.listar_por_usuario(id_usuario, limite)
    return jsonify(comentarios), 200

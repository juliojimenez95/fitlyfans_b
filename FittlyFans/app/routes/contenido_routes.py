from flasgger import swag_from
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from app.controllers.contenido_controller import ContenidoController
from app.utils.auth import token_required

contenido_bp = Blueprint("contenido", __name__)
contenido_controller = ContenidoController()

@contenido_bp.route("/contenidos", methods=["POST"])
@token_required
@swag_from('../../docs_api/contenido/crear_contenido.yml')
def crear_contenido(**kwargs):
    usuario_actual = kwargs.get('current_user')
    if request.is_json:
        data = request.get_json()
        id_usuario = data.get("id_usuario", usuario_actual['id'])
        descripcion = data.get("descripcion", "")
        url_archivo = None
    else:
        # FormData
        id_usuario = request.form.get("id_usuario", usuario_actual['id'])
        descripcion = request.form.get("descripcion", "")
        
        url_archivo = None
        if 'archivo' in request.files:
            file = request.files['archivo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads'))
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, unique_filename)
                file.save(file_path)
                url_archivo = unique_filename

    # Inferir tipo para el ENUM de la base de datos (video, imagen, texto)
    tipo_media = 'texto'
    if url_archivo:
        if url_archivo.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
            tipo_media = 'video'
        else:
            tipo_media = 'imagen'

    contenido_id = contenido_controller.crear(id_usuario, descripcion, tipo_media, url_archivo)
    return jsonify({"id": contenido_id}), 201 if contenido_id else 400

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["GET"])
@token_required
@swag_from('../../docs_api/contenido/obtener_contenido.yml')
def obtener_contenido(contenido_id, **kwargs):
    contenido = contenido_controller.obtener(contenido_id)
    return jsonify(contenido), 200 if contenido else 404

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["PUT"])
@token_required
@swag_from('../../docs_api/contenido/actualizar_contenido.yml')
def actualizar_contenido(contenido_id, **kwargs):
    data = request.get_json()
    descripcion = data.get("descripcion")
    exito = contenido_controller.actualizar(contenido_id, descripcion)
    return jsonify({"actualizado": exito}), 200 if exito else 400

@contenido_bp.route("/contenidos/<int:contenido_id>", methods=["DELETE"])
@token_required
@swag_from('../../docs_api/contenido/eliminar_contenido.yml')
def eliminar_contenido(contenido_id, **kwargs):
    exito = contenido_controller.eliminar(contenido_id)
    return jsonify({"eliminado": exito}), 200 if exito else 400

@contenido_bp.route("/contenidos/usuario/<int:id_usuario>", methods=["GET"])
@token_required
@swag_from('../../docs_api/contenido/listar_contenidos_por_usuario.yml')
def listar_contenidos_por_usuario(id_usuario, **kwargs):
    limite = int(request.args.get("limite", 50))
    offset = int(request.args.get("offset", 0))
    contenidos = contenido_controller.listar_por_usuario(id_usuario, limite, offset)
    return jsonify(contenidos), 200

@contenido_bp.route("/contenidos/tipo/<string:tipo>", methods=["GET"])
@token_required
@swag_from('../../docs_api/contenido/listar_contenidos_por_tipo.yml')
def listar_contenidos_por_tipo(tipo, **kwargs):
    limite = int(request.args.get("limite", 50))
    contenidos = contenido_controller.listar_por_tipo(tipo, limite)
    return jsonify(contenidos), 200

@contenido_bp.route("/contenidos/buscar", methods=["GET"])
@token_required
@swag_from('../../docs_api/contenido/buscar_contenido.yml')
def buscar_contenidos(**kwargs):
    termino = request.args.get("q", "")
    limite = int(request.args.get("limite", 50))
    contenidos = contenido_controller.buscar(termino, limite)
    return jsonify(contenidos), 200

@contenido_bp.route("/feed", methods=["GET"])
@token_required
def obtener_feed_premium(**kwargs):
    usuario_actual = kwargs.get('current_user')
    id_suscriptor = usuario_actual['id']
    limite = int(request.args.get("limite", 50))
    offset = int(request.args.get("offset", 0))
    
    # En listar_feed_suscriptor se asume que existe la validación de suscripciones
    contenidos = contenido_controller.listar_feed_suscriptor(id_suscriptor, limite, offset)
    return jsonify(contenidos), 200

@contenido_bp.route("/descubrir", methods=["GET"])
@token_required
def obtener_feed_descubrir(**kwargs):
    usuario_actual = kwargs.get('current_user')
    id_suscriptor = usuario_actual['id']
    limite = int(request.args.get("limite", 50))
    offset = int(request.args.get("offset", 0))
    
    contenidos = contenido_controller.listar_feed_descubrir(id_suscriptor, limite, offset)
    return jsonify(contenidos), 200

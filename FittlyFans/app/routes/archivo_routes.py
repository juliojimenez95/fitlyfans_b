from flask import Blueprint, send_from_directory, current_app, jsonify
import os

archivo_bp = Blueprint('archivos', __name__)

@archivo_bp.route('/<path:filename>')
def serve_file(filename):
    """
    Sirve archivos estáticos (imágenes, videos) almacenados localmente.
    """
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({"error": "Archivo no encontrado"}), 404

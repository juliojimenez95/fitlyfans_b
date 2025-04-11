from flask import jsonify

def registrar_manejadores_error(app):
    @app.errorhandler(500)
    def manejar_error_db(e):
        return jsonify({"error": "Error de base de datos", "mensaje": str(e)}), 500
        
    @app.errorhandler(404)
    def manejar_no_encontrado(e):
        return jsonify({"error": "Recurso no encontrado"}), 404
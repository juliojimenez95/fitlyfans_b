from flask import Blueprint, request, jsonify, current_app
from app.utils.auth import token_required
from app.controllers.progreso_controller import ProgresoController

progreso_bp = Blueprint('progreso', __name__)
progreso_controller = ProgresoController()

@progreso_bp.route('/finalizar-rutina', methods=['POST'])
@token_required
def finalizar_rutina(*args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'suscriptor':
            return jsonify({'error': 'No autorizado. Debes ser un suscriptor'}), 403

        data = request.json
        if not data or not data.get('rutina_id'):
            return jsonify({'error': 'rutina_id es requerido'}), 400

        exito = progreso_controller.registrar_rutina_completada(
            suscriptor_id=usuario['id'],
            rutina_id=data['rutina_id'],
            asignacion_plan_id=data.get('asignacion_plan_id'),
            semana=data.get('semana'),
            dia=data.get('dia'),
            duracion_segundos=data.get('duracion_segundos')
        )

        return jsonify({
            "success": exito,
            "message": "Rutina registrada correctamente" if exito else "Error al registrar la rutina"
        }), 200 if exito else 500

    except Exception as e:
        current_app.logger.error(f"Error al registrar progreso: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@progreso_bp.route('/suscriptor/<int:suscriptor_id>', methods=['GET'])
@token_required
def obtener_historial_suscriptor(suscriptor_id, *args, **kwargs):
    current_user = kwargs.get('current_user')
    # Validar que el usuario sea entrenador y tenga acceso a este suscriptor (se podría hacer, por ahora simplificamos)
    if not current_user or current_user.get('tipo_usuario') != 'trainer':
        return jsonify({"success": False, "message": "Acceso denegado"}), 403

    historial = progreso_controller.obtener_historial_suscriptor(suscriptor_id)
    return jsonify({
        "success": True,
        "historial": historial
    }), 200

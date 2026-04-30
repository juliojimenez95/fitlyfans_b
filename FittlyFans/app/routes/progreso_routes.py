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

        if exito:
            return jsonify({'mensaje': 'Rutina completada registrada con éxito'}), 200
        return jsonify({'error': 'No se pudo registrar la rutina'}), 400
    except Exception as e:
        current_app.logger.error(f"Error al registrar progreso: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

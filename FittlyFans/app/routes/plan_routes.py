from flask import Blueprint, request, jsonify, current_app
from flasgger import swag_from
from app.utils.auth import token_required
from app.controllers.plan_controller import PlanController

plan_bp = Blueprint('plan', __name__)
plan_controller = PlanController()

@plan_bp.route('', methods=['POST'])
@token_required
def crear_plan(*args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        data = request.json
        if not data or not data.get('nombre') or not data.get('duracion_semanas'):
            return jsonify({'error': 'Nombre y duracion_semanas son requeridos'}), 400

        plan_id = plan_controller.crear_plan(
            entrenador_id=usuario['id'],
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            objetivo=data.get('objetivo', ''),
            nivel=data.get('nivel', ''),
            duracion_semanas=data['duracion_semanas'],
            estado=data.get('estado', 'borrador')
        )

        return jsonify({'mensaje': 'Plan creado exitosamente', 'plan_id': plan_id}), 201
    except Exception as e:
        current_app.logger.error(f"Error al crear plan: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@plan_bp.route('/entrenador', methods=['GET'])
@token_required
def listar_planes_entrenador(*args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        planes = plan_controller.listar_planes_entrenador(usuario['id'])
        return jsonify({'planes': planes}), 200
    except Exception as e:
        current_app.logger.error(f"Error al listar planes: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@plan_bp.route('/<int:plan_id>', methods=['GET'])
@token_required
def obtener_plan(plan_id, *args, **kwargs):
    try:
        plan = plan_controller.obtener_plan(plan_id)
        if not plan:
            return jsonify({'error': 'Plan no encontrado'}), 404
            
        rutinas = plan_controller.listar_rutinas_de_plan(plan_id)
        plan['rutinas'] = rutinas
        return jsonify(plan), 200
    except Exception as e:
        current_app.logger.error(f"Error al obtener plan: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@plan_bp.route('/<int:plan_id>/rutina', methods=['POST'])
@token_required
def agregar_rutina_plan(plan_id, *args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        data = request.json
        if not data or not data.get('rutina_id') or not data.get('semana') or not data.get('dia'):
            return jsonify({'error': 'rutina_id, semana y dia son obligatorios'}), 400

        exito = plan_controller.agregar_rutina_a_plan(
            plan_id=plan_id,
            rutina_id=data['rutina_id'],
            semana=data['semana'],
            dia=data['dia']
        )
        if exito:
            return jsonify({'mensaje': 'Rutina asignada al plan correctamente'}), 200
        return jsonify({'error': 'No se pudo asignar la rutina'}), 400
    except Exception as e:
        current_app.logger.error(f"Error al asignar rutina a plan: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@plan_bp.route('/<int:plan_id>/asignar', methods=['POST'])
@token_required
def asignar_plan_suscriptor(plan_id, *args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'entrenador':
            return jsonify({'error': 'No autorizado. Debes ser un entrenador'}), 403

        data = request.json
        if not data or not data.get('suscriptor_id') or not data.get('fecha_inicio'):
            return jsonify({'error': 'suscriptor_id y fecha_inicio (YYYY-MM-DD) son obligatorios'}), 400

        exito = plan_controller.asignar_plan_suscriptor(
            plan_id=plan_id,
            suscriptor_id=data['suscriptor_id'],
            entrenador_id=usuario['id'],
            fecha_inicio=data['fecha_inicio']
        )
        if exito:
            return jsonify({'mensaje': 'Plan asignado exitosamente al suscriptor'}), 200
        return jsonify({'error': 'No se pudo asignar el plan'}), 400
    except Exception as e:
        current_app.logger.error(f"Error al asignar plan: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

@plan_bp.route('/mi-entrenamiento', methods=['GET'])
@token_required
def obtener_mi_entrenamiento(*args, **kwargs):
    try:
        usuario = kwargs.get('current_user')
        if not usuario or usuario.get('tipo_usuario') != 'suscriptor':
            return jsonify({'error': 'No autorizado. Debes ser un suscriptor'}), 403

        entrenamiento = plan_controller.obtener_entrenamiento_hoy(usuario['id'])
        if not entrenamiento:
            return jsonify({'mensaje': 'No tienes ningún plan activo', 'estado': 'sin_plan'}), 200
            
        return jsonify(entrenamiento), 200
    except Exception as e:
        current_app.logger.error(f"Error al obtener entrenamiento: {str(e)}")
        return jsonify({'error': 'Error interno del servidor', 'detalles': str(e)}), 500

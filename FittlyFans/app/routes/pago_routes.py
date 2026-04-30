from flasgger import swag_from
from flask import Blueprint, request, jsonify
from app.controllers.pago_controller import PagoController
from app.utils.auth import token_required

pago_bp = Blueprint('pago', __name__)
pago_controller = PagoController()

# Crear un nuevo pago
@pago_bp.route('', methods=['POST'])
@token_required
@swag_from('../../docs_api/pago/crear_pago.yml')
def crear_pago(*args, **kwargs):
    data = request.json

    id_suscripcion = data.get('id_suscripcion')
    monto = data.get('valor') # En el front es valor, en BD es monto
    if not monto:
        monto = data.get('monto')
    metodo_pago = data.get('metodo_pago', 'tarjeta')
    estado = data.get('estado', 'completado')
    descripcion = data.get('descripcion', 'Pago de suscripcion MVP')

    if not monto or not metodo_pago or not id_suscripcion:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    id_pago = pago_controller.crear(id_suscripcion, monto, metodo_pago, estado, descripcion)
    return jsonify({'mensaje': 'Pago registrado', 'id_pago': id_pago}), 201

# Obtener un pago por ID
@pago_bp.route('/<int:id_pago>', methods=['GET'])
@token_required
@swag_from('../../docs_api/pago/obtener_pago.yml')
def obtener_pago(id_pago, *args, **kwargs):
    pago = pago_controller.obtener(id_pago)
    if not pago:
        return jsonify({'error': 'Pago no encontrado'}), 404
    return jsonify(pago), 200

# Actualizar estado del pago
@pago_bp.route('/<int:id_pago>', methods=['PUT'])
@token_required
@swag_from('../../docs_api/pago/actualizar_estado_pago.yml')
def actualizar_estado_pago(id_pago, *args, **kwargs):
    data = request.json
    nuevo_estado = data.get('estado')
    descripcion = data.get('descripcion')

    if not nuevo_estado:
        return jsonify({'error': 'Falta el estado'}), 400

    actualizado = pago_controller.actualizar_estado(id_pago, nuevo_estado, descripcion)
    if not actualizado:
        return jsonify({'error': 'No se pudo actualizar el pago'}), 400

    return jsonify({'mensaje': 'Estado actualizado correctamente'}), 200

# Listar pagos de un suscriptor autenticado
@pago_bp.route('/mis-pagos', methods=['GET'])
@token_required
@swag_from('../../docs_api/pago/listar_mis_pagos.yml')
def listar_mis_pagos(*args, **kwargs):
    usuario = kwargs['current_user']
    pagos = pago_controller.listar_por_suscriptor(usuario['id'])
    return jsonify({'total': len(pagos), 'pagos': pagos}), 200

# Listar pagos por estado
@pago_bp.route('/estado/<string:estado>', methods=['GET'])
@token_required
@swag_from('../../docs_api/pago/listar_pagos_por_estado.yml')
def listar_pagos_por_estado(estado, *args, **kwargs):
    limite = request.args.get('limite', default=100, type=int)
    pagos = pago_controller.listar_por_estado(estado, limite)
    return jsonify({'total': len(pagos), 'pagos': pagos}), 200

# Obtener estadísticas de pagos
@pago_bp.route('/estadisticas', methods=['GET'])
@token_required
@swag_from('../../docs_api/pago/obtener_estadisticas.yml')
def obtener_estadisticas(*args, **kwargs):
    usuario = kwargs['current_user']
    solo_mios = request.args.get('mis_pagos', default='false').lower() == 'true'

    if solo_mios:
        stats = pago_controller.obtener_estadisticas(id_suscriptor=usuario['id'])
    else:
        stats = pago_controller.obtener_estadisticas()

    return jsonify(stats), 200

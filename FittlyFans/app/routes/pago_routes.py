from flask import Blueprint, request, jsonify
from app.controllers.pago_controller import PagoController
from app.utils.auth import token_required

pago_bp = Blueprint('pago', __name__)
pago_controller = PagoController()

# Crear un nuevo pago
@pago_bp.route('', methods=['POST'])
@token_required
def crear_pago(*args, **kwargs):
    usuario = kwargs['current_user']
    data = request.json

    id_suscriptor = usuario['id']
    monto = data.get('monto')
    metodo_pago = data.get('metodo_pago')
    estado = data.get('estado', 'pendiente')
    descripcion = data.get('descripcion')

    if not monto or not metodo_pago:
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    id_pago = pago_controller.crear(id_suscriptor, monto, metodo_pago, estado, descripcion)
    return jsonify({'mensaje': 'Pago registrado', 'id_pago': id_pago}), 201

# Obtener un pago por ID
@pago_bp.route('/<int:id_pago>', methods=['GET'])
@token_required
def obtener_pago(id_pago, *args, **kwargs):
    pago = pago_controller.obtener(id_pago)
    if not pago:
        return jsonify({'error': 'Pago no encontrado'}), 404
    return jsonify(pago), 200

# Actualizar estado del pago
@pago_bp.route('/<int:id_pago>', methods=['PUT'])
@token_required
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
def listar_mis_pagos(*args, **kwargs):
    usuario = kwargs['current_user']
    pagos = pago_controller.listar_por_suscriptor(usuario['id'])
    return jsonify({'total': len(pagos), 'pagos': pagos}), 200

# Listar pagos por estado
@pago_bp.route('/estado/<string:estado>', methods=['GET'])
@token_required
def listar_pagos_por_estado(estado, *args, **kwargs):
    limite = request.args.get('limite', default=100, type=int)
    pagos = pago_controller.listar_por_estado(estado, limite)
    return jsonify({'total': len(pagos), 'pagos': pagos}), 200

# Obtener estadísticas de pagos
@pago_bp.route('/estadisticas', methods=['GET'])
@token_required
def obtener_estadisticas(*args, **kwargs):
    usuario = kwargs['current_user']
    solo_mios = request.args.get('mis_pagos', default='false').lower() == 'true'

    if solo_mios:
        stats = pago_controller.obtener_estadisticas(id_suscriptor=usuario['id'])
    else:
        stats = pago_controller.obtener_estadisticas()

    return jsonify(stats), 200

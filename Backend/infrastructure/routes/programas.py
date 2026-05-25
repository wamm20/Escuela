from flask import Blueprint, request, jsonify
import jwt
import os
from domain.programas import (
    get_all_programas,
    get_programa_by_id,
    create_programa,
    update_programa,
    anular_programa,
    activar_programa,
)


programas_bp = Blueprint('programas', __name__)


@programas_bp.route('/programas', methods=['GET'])
def list_programas():
    try:
        programas = get_all_programas()
        return jsonify(programas), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@programas_bp.route('/programas/<int:id_program>', methods=['GET'])
def get_programa(id_program):
    try:
        programa = get_programa_by_id(id_program)
        if not programa:
            return jsonify({'message': 'Programa no encontrado'}), 404
        return jsonify(programa), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@programas_bp.route('/programas', methods=['POST'])
def create():
    data = request.get_json() or {}
    if not data.get('nombre_program'):
        return jsonify({'message': 'nombre_program es requerido'}), 400
    try:
        new_id = create_programa(data)
        return jsonify({'id_program': new_id, 'message': 'Programa creado'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@programas_bp.route('/programas/<int:id_program>', methods=['PUT'])
def update(id_program):
    data = request.get_json() or {}
    try:
        res = update_programa(id_program, data)
        if not res:
            return jsonify({'message': 'Programa no encontrado'}), 404
        return jsonify({'id_program': res, 'message': 'Programa actualizado'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@programas_bp.route('/programas/<int:id_program>', methods=['DELETE'])
def anular(id_program):
    try:
        res = anular_programa(id_program)
        if not res:
            return jsonify({'message': 'Programa no encontrado'}), 404
        return jsonify({'id_program': res, 'message': "Programa anulado (anu_prog='X')"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@programas_bp.route('/programas/<int:id_program>/activar', methods=['POST'])
def activar(id_program):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        jwt_secret = os.getenv('JWT_SECRET', 'change-this-secret')
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'], leeway=60)
            user_level = payload.get('user_level')
            if user_level is not None:
                user_level = int(user_level)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'message': 'Invalid or expired token'}), 401

        if user_level != 1:
            return jsonify({'message': 'Forbidden: requires admin level'}), 403

        res = activar_programa(id_program)
        if not res:
            return jsonify({'message': 'Programa no encontrado'}), 404
        return jsonify({'id_program': res, 'message': "Programa activado (anu_prog=NULL)"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
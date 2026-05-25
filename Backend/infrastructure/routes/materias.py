from flask import Blueprint, request, jsonify
import jwt
import os
from domain.materias import (
    get_all_materias,
    get_materia_by_id,
    create_materia,
    update_materia,
    anular_materia,
    activar_materia,
)

materias_bp = Blueprint('materias', __name__)


@materias_bp.route('/materias', methods=['GET'])
def list_materias():
    try:
        materias = get_all_materias()
        return jsonify(materias), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@materias_bp.route('/materias/<int:id_materia>', methods=['GET'])
def get_materia(id_materia):
    try:
        mat = get_materia_by_id(id_materia)
        if not mat:
            return jsonify({'message': 'Materia no encontrada'}), 404
        return jsonify(mat), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@materias_bp.route('/materias', methods=['POST'])
def create():
    data = request.get_json() or {}
    if not data.get('nombre_materia'):
        return jsonify({'message': 'nombre_materia es requerido'}), 400
    try:
        new_id = create_materia(data)
        return jsonify({'id_materia': new_id, 'message': 'Materia creada'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@materias_bp.route('/materias/<int:id_materia>', methods=['PUT'])
def update(id_materia):
    data = request.get_json() or {}
    try:
        res = update_materia(id_materia, data)
        if not res:
            return jsonify({'message': 'Materia no encontrada'}), 404
        return jsonify({'id_materia': res, 'message': 'Materia actualizada'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@materias_bp.route('/materias/<int:id_materia>', methods=['DELETE'])
def delete(id_materia):
    try:
        res = anular_materia(id_materia)
        if not res:
            return jsonify({'message': 'Materia no encontrada'}), 404
        return jsonify({'id_materia': res, 'message': "Materia anulada (anu_mat='X')"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@materias_bp.route('/materias/<int:id_materia>/activar', methods=['POST'])
def activar(id_materia):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401
        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
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

        res = activar_materia(id_materia)
        if not res:
            return jsonify({'message': 'Materia no encontrada'}), 404
        return jsonify({'id_materia': res, 'message': "Materia activada (anu_mat=NULL)"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

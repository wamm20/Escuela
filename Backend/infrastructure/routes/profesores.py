from flask import Blueprint, request, jsonify
from domain.profesores import (
    get_all_profesores,
    get_profesor_by_id,
    create_profesor,
    update_profesor,
    anular_profesor,
    activar_profesor,
)

profesores_bp = Blueprint('profesores', __name__)


@profesores_bp.route('/profesores', methods=['GET'])
def list_profesores():
    try:
        profesores = get_all_profesores()
        return jsonify(profesores), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@profesores_bp.route('/profesores/<int:id_profesor>', methods=['GET'])
def get_profesor(id_profesor):
    try:
        profesor = get_profesor_by_id(id_profesor)
        if not profesor:
            return jsonify({'message': 'Profesor no encontrado'}), 404
        return jsonify(profesor), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@profesores_bp.route('/profesores', methods=['POST'])
def create():
    data = request.get_json() or {}
    if not data.get('nombre') or not data.get('apellido'):
        return jsonify({'message': 'nombre y apellido son requeridos'}), 400
    try:
        new_id = create_profesor(data)
        return jsonify({'id_profesor': new_id, 'message': 'Profesor creado'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@profesores_bp.route('/profesores/<int:id_profesor>', methods=['PUT'])
def update(id_profesor):
    data = request.get_json() or {}
    try:
        res = update_profesor(id_profesor, data)
        if not res:
            return jsonify({'message': 'Profesor no encontrado'}), 404
        return jsonify({'id_profesor': res, 'message': 'Profesor actualizado'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@profesores_bp.route('/profesores/<int:id_profesor>', methods=['DELETE'])
def anular(id_profesor):
    try:
        res = anular_profesor(id_profesor)
        if not res:
            return jsonify({'message': 'Profesor no encontrado'}), 404
        return jsonify({'id_profesor': res, 'message': "Profesor anulado (anu_prof='X')"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@profesores_bp.route('/profesores/<int:id_profesor>/activar', methods=['POST'])
def activar(id_profesor):
    try:
        # Verificar token y permisos (solo nivel 1)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        import jwt, os
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

        res = activar_profesor(id_profesor)
        if not res:
            return jsonify({'message': 'Profesor no encontrado'}), 404
        return jsonify({'id_profesor': res, 'message': "Profesor activado (anu_prof=NULL)"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

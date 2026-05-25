from flask import Blueprint, request, jsonify
import jwt
import os
from domain.alumnos import get_all_alumnos, get_alumno_by_id, create_alumno, update_alumno, anular_alumno, activar_alumno

alumnos_bp = Blueprint('alumnos', __name__)


@alumnos_bp.route('/alumnos', methods=['GET'])
def list_alumnos():
    try:
        alumnos = get_all_alumnos()
        return jsonify(alumnos), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@alumnos_bp.route('/alumnos/<int:id_alumno>', methods=['GET'])
def get_alumno(id_alumno):
    try:
        alumno = get_alumno_by_id(id_alumno)
        if not alumno:
            return jsonify({'message': 'Alumno no encontrado'}), 404
        return jsonify(alumno), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@alumnos_bp.route('/alumnos', methods=['POST'])
def create():
    data = request.get_json() or {}
    # Validaciones mínimas
    if not data.get('nombre') or not data.get('apellido'):
        return jsonify({'message': 'nombre y apellido son requeridos'}), 400
    try:
        new_id = create_alumno(data)
        return jsonify({'id_alumno': new_id, 'message': 'Alumno creado'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@alumnos_bp.route('/alumnos/<int:id_alumno>', methods=['PUT'])
def update(id_alumno):
    data = request.get_json() or {}
    try:
        res = update_alumno(id_alumno, data)
        if not res:
            return jsonify({'message': 'Alumno no encontrado'}), 404
        return jsonify({'id_alumno': res, 'message': 'Alumno actualizado'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@alumnos_bp.route('/alumnos/<int:id_alumno>', methods=['DELETE'])
def delete(id_alumno):
    try:
        res = anular_alumno(id_alumno)
        if not res:
            return jsonify({'message': 'Alumno no encontrado'}), 404
        return jsonify({'id_alumno': res, 'message': "Alumno anulado (anu_alum='X')"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@alumnos_bp.route('/alumnos/<int:id_alumno>/activar', methods=['POST'])
def activar(id_alumno):
    try:
        # Verificar token y permisos (solo nivel 1)
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

        res = activar_alumno(id_alumno)
        if not res:
            return jsonify({'message': 'Alumno no encontrado'}), 404
        return jsonify({'id_alumno': res, 'message': "Alumno activado (anu_alum=NULL)"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

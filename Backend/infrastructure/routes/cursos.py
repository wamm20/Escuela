from flask import Blueprint, request, jsonify
import jwt
import os
from domain.cursos import (
    get_all_cursos,
    get_curso_by_id,
    create_curso,
    update_curso,
    anular_curso,
    activar_curso,
)
from domain.curso_materia import (
    get_materias_por_curso,
    add_or_update_asignacion,
    anular_asignacion,
    activar_asignacion,
)

cursos_bp = Blueprint('cursos', __name__)


@cursos_bp.route('/cursos', methods=['GET'])
def list_cursos():
    try:
        cursos = get_all_cursos()
        return jsonify(cursos), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>', methods=['GET'])
def get_curso(id_curso):
    try:
        c = get_curso_by_id(id_curso)
        if not c:
            return jsonify({'message': 'Curso no encontrado'}), 404
        return jsonify(c), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos', methods=['POST'])
def create():
    data = request.get_json() or {}
    for campo in ('nombre_curso', 'anio_escolar', 'fecha_inicio', 'fecha_fin'):
        if not data.get(campo):
            return jsonify({'message': f'{campo} es requerido'}), 400
    try:
        new_id = create_curso(data)
        return jsonify({'id_curso': new_id, 'message': 'Curso creado'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>', methods=['PUT'])
def update(id_curso):
    data = request.get_json() or {}
    try:
        res = update_curso(id_curso, data)
        if not res:
            return jsonify({'message': 'Curso no encontrado'}), 404
        return jsonify({'id_curso': res, 'message': 'Curso actualizado'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>', methods=['DELETE'])
def delete(id_curso):
    try:
        res = anular_curso(id_curso)
        if not res:
            return jsonify({'message': 'Curso no encontrado'}), 404
        return jsonify({'id_curso': res, 'message': "Curso anulado (anu_cur='X')"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>/activar', methods=['POST'])
def activar(id_curso):
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

        res = activar_curso(id_curso)
        if not res:
            return jsonify({'message': 'Curso no encontrado'}), 404
        return jsonify({'id_curso': res, 'message': "Curso activado (anu_cur=NULL)"}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# curso-materia endpoints ------------------------------------------------
@cursos_bp.route('/cursos/<int:id_curso>/materias', methods=['GET'])
def list_curso_materias(id_curso):
    try:
        asignaciones = get_materias_por_curso(id_curso)
        return jsonify(asignaciones), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>/materias', methods=['POST'])
def add_curso_materias(id_curso):
    data = request.get_json() or []
    if not isinstance(data, list):
        return jsonify({'message': 'payload debe ser una lista de asignaciones'}), 400
    try:
        results = []
        for item in data:
            mid = item.get('id_materia')
            pid = item.get('id_profesor')
            if mid is None or pid is None:
                raise ValueError('cada asignación necesita id_materia e id_profesor')
            new_id = add_or_update_asignacion(id_curso, mid, pid)
            results.append(new_id)
        return jsonify({'ids': results}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>/materias/<int:id_cm>/anular', methods=['POST'])
def anular_curso_materia(id_curso, id_cm):
    try:
        res = anular_asignacion(id_cm)
        if not res:
            return jsonify({'message': 'Asignación no encontrada'}), 404
        return jsonify({'id_curso_materia': res, 'message': 'Asignación anulada'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@cursos_bp.route('/cursos/<int:id_curso>/materias/<int:id_cm>/activar', methods=['POST'])
def activar_curso_materia(id_curso, id_cm):
    try:
        res = activar_asignacion(id_cm)
        if not res:
            return jsonify({'message': 'Asignación no encontrada'}), 404
        return jsonify({'id_curso_materia': res, 'message': 'Asignación activada'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

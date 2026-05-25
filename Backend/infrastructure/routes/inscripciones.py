from flask import Blueprint, request, jsonify
from domain.inscripciones import (
    get_alumnos_disponibles_por_curso,
    get_inscripciones_por_curso,
    add_inscripciones,
    suspend_inscripciones,
    activate_inscripciones,
)


inscripciones_bp = Blueprint('inscripciones', __name__)


@inscripciones_bp.route('/inscripciones/cursos/<int:id_curso>', methods=['GET'])
def get_estado_curso(id_curso):
    try:
        return jsonify({
            'disponibles': get_alumnos_disponibles_por_curso(id_curso),
            'inscritos': get_inscripciones_por_curso(id_curso),
        }), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@inscripciones_bp.route('/inscripciones/cursos/<int:id_curso>', methods=['POST'])
def create_inscripciones(id_curso):
    data = request.get_json() or {}
    alumno_ids = data.get('alumnos', [])
    try:
        ids = add_inscripciones(id_curso, alumno_ids)
        return jsonify({'ids': ids, 'message': 'Inscripciones creadas'}), 201
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@inscripciones_bp.route('/inscripciones/cursos/<int:id_curso>/anular', methods=['POST'])
def anular_inscripciones(id_curso):
    data = request.get_json() or {}
    inscripcion_ids = data.get('inscripciones', [])
    try:
        ids = suspend_inscripciones(id_curso, inscripcion_ids)
        return jsonify({'ids': ids, 'message': 'Inscripciones suspendidas'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@inscripciones_bp.route('/inscripciones/cursos/<int:id_curso>/activar', methods=['POST'])
def activar_inscripciones(id_curso):
    data = request.get_json() or {}
    inscripcion_ids = data.get('inscripciones', [])
    try:
        ids = activate_inscripciones(id_curso, inscripcion_ids)
        return jsonify({'ids': ids, 'message': 'Inscripciones activadas'}), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500
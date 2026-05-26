from flask import Blueprint, jsonify, request

from domain.calificaciones import get_estado_calificaciones_por_curso, save_calificacion


calificaciones_bp = Blueprint('calificaciones', __name__)


@calificaciones_bp.route('/calificaciones/cursos/<int:id_curso>', methods=['GET'])
def get_estado_calificaciones(id_curso):
    try:
        return jsonify(get_estado_calificaciones_por_curso(id_curso)), 200
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@calificaciones_bp.route('/calificaciones', methods=['POST'])
def create_or_update_calificacion():
    data = request.get_json() or {}
    try:
        result = save_calificacion(data)
        status = 201 if result.get('action') == 'created' else 200
        message = 'Calificación creada' if result.get('action') == 'created' else 'Calificación actualizada'
        return jsonify({**result, 'message': message}), status
    except ValueError as ve:
        return jsonify({'message': str(ve)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500
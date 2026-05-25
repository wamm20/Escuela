from flask import Blueprint, request, jsonify
from domain.Configuration.database import get_db_connection
import bcrypt

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_usuario, ci_usuario, nom_usuario, ape_usuario, nvl_usuario, cargo_usuario, usuario FROM escuela.usuarios ORDER BY id_usuario ASC")
            rows = cur.fetchall()
            users = []
            for row in rows:
                users.append({
                    'id_usuario': row[0],
                    'ci_usuario': row[1],
                    'nom_usuario': row[2],
                    'ape_usuario': row[3],
                    'nvl_usuario': row[4],
                    'cargo_usuario': row[5],
                    'usuario': row[6]
                })
            return jsonify(users), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@users_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # Aquí deberías agregar validaciones de campos requeridos
    
    password = data.get('password')
    if not password:
        return jsonify({'message': 'Password is required'}), 400

    # Encriptar contraseña
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Se guarda SOLO en pwr_usuario_hash. pwr_usuario_plain se omite (quedará NULL).
            cur.execute("""
                INSERT INTO escuela.usuarios 
                (ci_usuario, nom_usuario, ape_usuario, nvl_usuario, cargo_usuario, usuario, pwr_usuario_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_usuario
            """, (data['ci_usuario'], data['nom_usuario'], data['ape_usuario'], 
                  data['nvl_usuario'], data['cargo_usuario'], data['usuario'], hashed_pw))
            user_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({'id_usuario': user_id, 'message': 'Usuario creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
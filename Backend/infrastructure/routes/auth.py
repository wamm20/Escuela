from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
import logging
import sys
from domain.Configuration.database import get_db_connection

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        jwt_secret = os.getenv('JWT_SECRET', 'change-this-secret')
        jwt_algo = 'HS256'
        jwt_expire_minutes = int(os.getenv('JWT_EXPIRE_MINUTES', 1440))

        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if username:
            username = username.upper()

        logging.info(f"Intento de login para el usuario: '{username}'")

        if not username or not password:
            return jsonify({'message': 'username and password required'}), 400

        with get_db_connection() as conn:
            if not conn:
                return jsonify({'message': 'database connection error'}), 500
            cur = conn.cursor()

            # Se obtienen todos los campos necesarios, incluyendo el estado (anu_usu) y el nivel (nvl_usuario)
            cur.execute("""
                SELECT 
                    id_usuario, usuario, nom_usuario, ape_usuario,
                    pwr_usuario_hash, pwr_usuario_plain, anu_usu, nvl_usuario
                FROM escuela.usuarios 
                WHERE usuario = %s
            """, (username,))
            
            user_data = cur.fetchone()
            cur.close()

            if not user_data:
                logging.warning(f"Fallo de login: Usuario '{username}' no encontrado en la base de datos.")
                return jsonify({'message': 'invalid credentials'}), 401

            # Mapear la tupla a un diccionario para un acceso más claro
            user = {
                'id': user_data[0],
                'username': user_data[1],
                'nom_usuario': user_data[2],
                'ape_usuario': user_data[3],
                'pwr_hash': user_data[4],
                'pwr_plain': user_data[5],
                'anu_usu': user_data[6],
                'user_level': int(user_data[7]) if user_data[7] is not None else None
            }

            logging.debug(f"Usuario '{username}' encontrado (ID: {user['id']}). Verificando estado y contraseña.")

            # REQUISITO 1: Verificar si el usuario está anulado/bloqueado
            if user['anu_usu'] == 'X':
                logging.warning(f"Acceso denegado: El usuario '{username}' está bloqueado (anu_usu='X').")
                return jsonify({'message': 'Acceso Denegado'}), 401

            # Lógica de validación de contraseña simplificada
            password_valid = False
            # Prioridad 1: Verificar con hash bcrypt si existe
            if user['pwr_hash']:
                logging.debug(f"Verificando contraseña para '{username}' usando hash bcrypt.")
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), user['pwr_hash'].encode('utf-8')):
                        password_valid = True
                        logging.debug(f"Contraseña bcrypt VÁLIDA para '{username}'.")
                    else:
                        logging.warning(f"Fallo de login: Contraseña bcrypt INCORRECTA para '{username}'.")
                except (ValueError, TypeError) as e:
                    logging.error(f"Error al verificar hash para '{username}': {e}. El hash podría estar malformado.")
                    password_valid = False
            # Prioridad 2: Fallback a texto plano (para transición)
            elif user['pwr_plain'] and user['pwr_plain'] == password:
                logging.debug(f"Verificando contraseña para '{username}' usando texto plano (fallback).")
                password_valid = True
            else:
                logging.error(f"Fallo de login: No se encontró un método de contraseña válido (hash o plain) para '{username}'.")

            if not password_valid:
                # El log específico (incorrecta o no encontrada) ya se emitió arriba
                return jsonify({'message': 'invalid credentials'}), 401

            # REQUISITO 2: Incluir el nivel del usuario en el token JWT
            payload = {
                'sub': str(user['id']),
                'username': user['username'],
                'nom_usuario': user['nom_usuario'],
                'ape_usuario': user['ape_usuario'],
                'user_level': user['user_level'],
                'exp': datetime.utcnow() + timedelta(minutes=jwt_expire_minutes)
            }
            logging.info(f"Login exitoso para '{username}'. Generando token JWT.")
            token = jwt.encode(payload, jwt_secret, algorithm=jwt_algo)
            return jsonify({'access_token': token}), 200

    except Exception as e:
        # Captura cualquier excepción no controlada para diagnosticar el error 500.
        # Imprime en stderr para asegurar que sea visible en la consola del servidor.
        error_message = f"ERROR INESPERADO en /api/login: {e}"
        print(error_message, file=sys.stderr)
        
        # También usa logging por si está configurado para ir a un archivo.
        logging.exception(error_message)
        
        return jsonify({'message': 'Error interno del servidor. Revise los logs del backend.'}), 500

@auth_bp.route('/users', methods=['GET'])
def get_users():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        jwt_secret = os.getenv('JWT_SECRET', 'change-this-secret')

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'], leeway=60)
            user_level = payload.get('user_level')
            # Asegurar que user_level sea entero para la comparación
            if user_level is not None:
                user_level = int(user_level)

            # El claim 'sub' se almacenó como string por compatibilidad con PyJWT
            user_id = int(payload.get('sub')) if payload.get('sub') is not None else None
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'message': 'Invalid or expired token'}), 401

        with get_db_connection() as conn:
            cur = conn.cursor()
            if user_level == 1:
                cur.execute("SELECT id_usuario, ci_usuario, nom_usuario, ape_usuario, nvl_usuario, cargo_usuario, usuario, anu_usu FROM escuela.usuarios ORDER BY id_usuario ASC")
            else:
                cur.execute("""
                    SELECT id_usuario, ci_usuario, nom_usuario, ape_usuario, nvl_usuario, cargo_usuario, usuario, anu_usu 
                    FROM escuela.usuarios WHERE id_usuario = %s ORDER BY id_usuario ASC
                """, (user_id,))
            
            rows = cur.fetchall()
            cur.close()
            
            users = []
            for row in rows:
                users.append({
                    'id_usuario': row[0],
                    'ci_usuario': row[1],
                    'nom_usuario': row[2],
                    'ape_usuario': row[3],
                    'nvl_usuario': row[4],
                    'cargo_usuario': row[5],
                    'usuario': row[6],
                    'anu_usu': row[7]
                })
            return jsonify(users), 200
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        return jsonify({'message': 'Error retrieving users'}), 500

@auth_bp.route('/users/<int:id_usuario>', methods=['PUT'])
def update_user(id_usuario):
    try:
        # Verificar Token y Permisos
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        jwt_secret = os.getenv('JWT_SECRET', 'change-this-secret')

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'], leeway=60)
            requester_level = payload.get('user_level')
            requester_id = int(payload.get('sub')) if payload.get('sub') is not None else None
            if requester_level is not None:
                requester_level = int(requester_level)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'message': 'Invalid or expired token'}), 401

        # Regla: Solo admin (1) puede editar a otros. Usuarios normales solo a sí mismos.
        if requester_level != 1 and requester_id != id_usuario:
            return jsonify({'message': 'Unauthorized: You can only modify your own profile'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Obtener datos actuales para validar existencia y proteger campos sensibles
            cur.execute("SELECT id_usuario, nvl_usuario, anu_usu FROM escuela.usuarios WHERE id_usuario = %s", (id_usuario,))
            current_user = cur.fetchone()
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
            
            sql = """
                UPDATE escuela.usuarios 
                SET ci_usuario = %s, nom_usuario = %s, ape_usuario = %s, 
                    nvl_usuario = %s, cargo_usuario = %s, usuario = %s, anu_usu = %s
                WHERE id_usuario = %s
            """

            # Regla: Si no es admin, forzar que nvl_usuario y anu_usu sean los que ya tiene en BD
            if requester_level != 1:
                data['nvl_usuario'] = current_user[1]
                data['anu_usu'] = current_user[2]
            
            # Función auxiliar para convertir a mayúsculas si es texto
            def to_upper(val):
                return val.upper() if isinstance(val, str) else val

            password = data.get('password')

            if password:
                # Si se envía contraseña, solo actualizamos el hash, NO el texto plano.
                # La contraseña NO se convierte a mayúsculas.
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                sql = """
                    UPDATE escuela.usuarios 
                    SET ci_usuario = %s, nom_usuario = %s, ape_usuario = %s, 
                        nvl_usuario = %s, cargo_usuario = %s, usuario = %s, anu_usu = %s,
                        pwr_usuario_hash = %s
                    WHERE id_usuario = %s
                """
                cur.execute(sql, (
                    to_upper(data.get('ci_usuario')), to_upper(data.get('nom_usuario')), to_upper(data.get('ape_usuario')),
                    data.get('nvl_usuario'), to_upper(data.get('cargo_usuario')), to_upper(data.get('usuario')),
                    to_upper(data.get('anu_usu')), 
                    hashed_pw,
                    id_usuario
                ))
            else:
                # Si no hay contraseña, usamos la consulta original
                cur.execute(sql, (
                    to_upper(data.get('ci_usuario')), to_upper(data.get('nom_usuario')), to_upper(data.get('ape_usuario')),
                    data.get('nvl_usuario'), to_upper(data.get('cargo_usuario')), to_upper(data.get('usuario')),
                    to_upper(data.get('anu_usu')), id_usuario
                ))

            conn.commit()
            return jsonify({'message': 'User updated successfully'}), 200

    except Exception as e:
        logging.error(f"Error updating user {id_usuario}: {e}")
        return jsonify({'message': 'Error updating user'}), 500

@auth_bp.route('/users', methods=['POST'])
def create_user():
    try:
        # 1. Verificar Token y Nivel (Seguridad)
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token missing'}), 401

        token = auth_header.split(" ")[1] if " " in auth_header else auth_header
        jwt_secret = os.getenv('JWT_SECRET', 'change-this-secret')

        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'], leeway=60)
        if payload.get('user_level') != 1:
            return jsonify({'message': 'Unauthorized: Only level 1 users can create users'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        # Validar campos obligatorios
        required = ['usuario', 'password', 'ci_usuario', 'nom_usuario', 'ape_usuario', 'nvl_usuario', 'cargo_usuario']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'message': f'Field {field} is required'}), 400

        def to_upper(val):
            return val.upper() if isinstance(val, str) else val

        username = to_upper(data['usuario'])
        password = data['password'] # La contraseña se mantiene tal cual (case sensitive)
        
        # Encriptar password para pwr_usuario_hash
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Verificar duplicados
            cur.execute("SELECT id_usuario FROM escuela.usuarios WHERE usuario = %s", (username,))
            if cur.fetchone():
                return jsonify({'message': 'El usuario ya existe'}), 409

            # No guardamos nada en pwr_usuario_plain
            sql = """
                INSERT INTO escuela.usuarios 
                (ci_usuario, nom_usuario, ape_usuario, nvl_usuario, cargo_usuario, usuario, pwr_usuario_hash, anu_usu)
                VALUES (%s, %s, %s, %s, %s, %s, %s, '')
                RETURNING id_usuario
            """
            
            cur.execute(sql, (
                to_upper(data['ci_usuario']), 
                to_upper(data['nom_usuario']), 
                to_upper(data['ape_usuario']),
                data['nvl_usuario'], 
                to_upper(data['cargo_usuario']), 
                username,
                hashed_pw
            ))
            
            new_id = cur.fetchone()[0]
            conn.commit()
            return jsonify({'message': 'User created successfully', 'id_usuario': new_id}), 201

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({'message': 'Invalid or expired token'}), 401
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        return jsonify({'message': 'Error creating user'}), 500

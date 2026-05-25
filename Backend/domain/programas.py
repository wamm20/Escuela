from domain.Configuration.database import get_db_connection


def _to_upper_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    return value


NOMBRE_MAX = 255


def _validate_and_normalize(data: dict, is_update=False):
    out = {}

    if not is_update and not data.get('nombre_program'):
        raise ValueError('nombre_program es requerido')

    if 'nombre_program' in data:
        nombre = data.get('nombre_program')
        if nombre is None or str(nombre).strip() == '':
            nombre = None
        else:
            nombre = _to_upper_str(nombre)
            if len(nombre) > NOMBRE_MAX:
                raise ValueError(f'nombre_program supera {NOMBRE_MAX} caracteres')
        out['nombre_program'] = nombre

    return out


def get_all_programas():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_program, nombre_program, anu_prog FROM escuela.program ORDER BY id_program ASC"
            )
            rows = cur.fetchall()
            programas = []
            for row in rows:
                programas.append({
                    'id_program': row[0],
                    'nombre_program': row[1],
                    'anu_prog': row[2],
                })
            return programas
    except Exception:
        raise


def get_programa_by_id(id_program):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_program, nombre_program, anu_prog FROM escuela.program WHERE id_program = %s",
                (id_program,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                'id_program': row[0],
                'nombre_program': row[1],
                'anu_prog': row[2],
            }
    except Exception:
        raise


def create_programa(data: dict):
    vals = _validate_and_normalize(data, is_update=False)
    nombre = vals.get('nombre_program')

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO escuela.program (nombre_program, anu_prog)
                VALUES (%s, NULL)
                RETURNING id_program
                """,
                (nombre,)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise


def update_programa(id_program, data: dict):
    vals = _validate_and_normalize(data, is_update=True)
    nombre = vals.get('nombre_program') if 'nombre_program' in vals else None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE escuela.program
                SET nombre_program = COALESCE(%s, nombre_program)
                WHERE id_program = %s
                RETURNING id_program
                """,
                (nombre, id_program)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def anular_programa(id_program):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.program SET anu_prog = 'X' WHERE id_program = %s RETURNING id_program",
                (id_program,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_programa(id_program):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.program SET anu_prog = NULL WHERE id_program = %s RETURNING id_program",
                (id_program,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise
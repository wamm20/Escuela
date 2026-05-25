from domain.Configuration.database import get_db_connection


def _to_upper_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    return value


# Constraint that matches the DB schema
NOMBRE_MAX = 255


def _validate_and_normalize(data: dict, is_update=False):
    """Validate/normalize input dictionary.
    When is_update=True missing keys are ignored (kept as None for COALESCE).
    Raises ValueError on violation and returns normalized dict.
    """
    out = {}

    # nombre_materia required on creation
    if not is_update:
        if not data.get('nombre_materia'):
            raise ValueError('nombre_materia es requerido')

    if 'nombre_materia' in data:
        nombre = data.get('nombre_materia')
        if nombre is None or str(nombre).strip() == '':
            nombre = None
        else:
            nombre = _to_upper_str(nombre)
            if len(nombre) > NOMBRE_MAX:
                raise ValueError(f'nombre_materia supera {NOMBRE_MAX} caracteres')
        out['nombre_materia'] = nombre

    return out


# CRUD helpers --------------------------------------------------------------

def get_all_materias():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_materia, nombre_materia, anu_mat FROM escuela.materias ORDER BY id_materia ASC"
            )
            rows = cur.fetchall()
            materias = []
            for r in rows:
                materias.append({
                    'id_materia': r[0],
                    'nombre_materia': r[1],
                    'anu_mat': r[2]
                })
            return materias
    except Exception:
        raise


def get_materia_by_id(id_materia):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_materia, nombre_materia, anu_mat FROM escuela.materias WHERE id_materia = %s",
                (id_materia,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id_materia': r[0],
                'nombre_materia': r[1],
                'anu_mat': r[2]
            }
    except Exception:
        raise


def create_materia(data: dict):
    vals = _validate_and_normalize(data, is_update=False)
    nombre = vals.get('nombre_materia')
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO escuela.materias (nombre_materia, anu_mat)
                VALUES (%s, NULL)
                RETURNING id_materia
                """,
                (nombre,)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise


def update_materia(id_materia, data: dict):
    vals = _validate_and_normalize(data, is_update=True)
    nombre = vals.get('nombre_materia') if 'nombre_materia' in vals else None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE escuela.materias
                SET nombre_materia = COALESCE(%s, nombre_materia)
                WHERE id_materia = %s
                RETURNING id_materia
                """,
                (nombre, id_materia)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def anular_materia(id_materia):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.materias SET anu_mat = 'X' WHERE id_materia = %s RETURNING id_materia",
                (id_materia,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_materia(id_materia):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.materias SET anu_mat = NULL WHERE id_materia = %s RETURNING id_materia",
                (id_materia,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

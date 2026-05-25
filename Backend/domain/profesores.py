from domain.Configuration.database import get_db_connection
from datetime import datetime


def _to_upper_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    return value


# Límites que coinciden con el esquema de BD
NOMBRE_MAX = 100
APELLIDO_MAX = 100
ESPECIALIDAD_MAX = 255
EMAIL_MAX = 255
CEDULA_MAX = 8


def _validate_and_normalize(data: dict, is_update=False):
    out = {}

    # nombre/apellido requeridos en creación
    if not is_update:
        if not data.get('nombre'):
            raise ValueError('nombre es requerido')
        if not data.get('apellido'):
            raise ValueError('apellido es requerido')

    if 'nombre' in data:
        nombre = data.get('nombre')
        if nombre is None or str(nombre).strip() == '':
            nombre = None
        else:
            nombre = _to_upper_str(nombre)
            if len(nombre) > NOMBRE_MAX:
                raise ValueError(f'nombre supera {NOMBRE_MAX} caracteres')
        out['nombre'] = nombre

    if 'apellido' in data:
        apellido = data.get('apellido')
        if apellido is None or str(apellido).strip() == '':
            apellido = None
        else:
            apellido = _to_upper_str(apellido)
            if len(apellido) > APELLIDO_MAX:
                raise ValueError(f'apellido supera {APELLIDO_MAX} caracteres')
        out['apellido'] = apellido

    # Cedula del profesor: aceptar número o string de dígitos
    if 'cedula_prof' in data:
        ced = data.get('cedula_prof')
        if ced is None or (isinstance(ced, str) and ced.strip() == ''):
            cedula = None
        else:
            ced_str = str(ced).strip()
            if not ced_str.isdigit():
                raise ValueError('cedula_prof debe ser numérica')
            if len(ced_str) > CEDULA_MAX:
                raise ValueError(f'cedula_prof supera {CEDULA_MAX} dígitos')
            cedula = int(ced_str)
        out['cedula_prof'] = cedula

    if 'especialidad' in data:
        esp = data.get('especialidad')
        if esp is None or str(esp).strip() == '':
            esp = None
        else:
            esp = _to_upper_str(esp)
            if len(esp) > ESPECIALIDAD_MAX:
                raise ValueError(f'especialidad supera {ESPECIALIDAD_MAX} caracteres')
        out['especialidad'] = esp

    if 'email' in data:
        em = data.get('email')
        if em is None or str(em).strip() == '':
            em = None
        else:
            em = _to_upper_str(em)
            if len(em) > EMAIL_MAX:
                raise ValueError(f'email supera {EMAIL_MAX} caracteres')
            # validación mínima de formato (el carácter @ no cambia con upper)
            if '@' not in em:
                raise ValueError('email inválido')
        out['email'] = em

    return out


def get_all_profesores():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_profesor, nombre, apellido, cedula_prof, especialidad, email, anu_prof FROM escuela.profesores ORDER BY id_profesor ASC")
            rows = cur.fetchall()
            profesores = []
            for r in rows:
                profesores.append({
                    'id_profesor': r[0],
                    'nombre': r[1],
                    'apellido': r[2],
                    'cedula_prof': int(r[3]) if r[3] is not None else None,
                    'especialidad': r[4],
                    'email': r[5],
                    'anu_prof': r[6]
                })
            return profesores
    except Exception:
        raise


def get_profesor_by_id(id_profesor):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_profesor, nombre, apellido, cedula_prof, especialidad, email, anu_prof FROM escuela.profesores WHERE id_profesor = %s", (id_profesor,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id_profesor': r[0],
                'nombre': r[1],
                'apellido': r[2],
                'cedula_prof': int(r[3]) if r[3] is not None else None,
                'especialidad': r[4],
                'email': r[5],
                'anu_prof': r[6]
            }
    except Exception:
        raise


def create_profesor(data: dict):
    vals = _validate_and_normalize(data, is_update=False)

    nombre = vals.get('nombre')
    apellido = vals.get('apellido')
    cedula_prof = vals.get('cedula_prof')
    especialidad = vals.get('especialidad')
    email = vals.get('email')

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO escuela.profesores (nombre, apellido, cedula_prof, especialidad, email, anu_prof)
                VALUES (%s, %s, %s, %s, %s, NULL)
                RETURNING id_profesor
                """,
                (nombre, apellido, cedula_prof, especialidad, email)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise


def update_profesor(id_profesor, data: dict):
    vals = _validate_and_normalize(data, is_update=True)

    nombre = vals.get('nombre') if 'nombre' in vals else None
    apellido = vals.get('apellido') if 'apellido' in vals else None
    cedula_prof = vals.get('cedula_prof') if 'cedula_prof' in vals else None
    especialidad = vals.get('especialidad') if 'especialidad' in vals else None
    email = vals.get('email') if 'email' in vals else None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE escuela.profesores
                SET nombre = COALESCE(%s, nombre),
                    apellido = COALESCE(%s, apellido),
                    cedula_prof = COALESCE(%s, cedula_prof),
                    especialidad = COALESCE(%s, especialidad),
                    email = COALESCE(%s, email)
                WHERE id_profesor = %s
                RETURNING id_profesor
                """,
                (nombre, apellido, cedula_prof, especialidad, email, id_profesor)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def anular_profesor(id_profesor):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE escuela.profesores SET anu_prof = 'X' WHERE id_profesor = %s RETURNING id_profesor", (id_profesor,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_profesor(id_profesor):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE escuela.profesores SET anu_prof = NULL WHERE id_profesor = %s RETURNING id_profesor", (id_profesor,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

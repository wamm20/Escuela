from domain.Configuration.database import get_db_connection
from datetime import datetime

def _to_upper_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    return value


# Reglas y límites que coinciden con el frontend / esquema de BD
NOMBRE_MAX = 100
APELLIDO_MAX = 100
DIRECCION_MAX = 255
TELEFONO_MAX = 20
CEDULA_MAX = 8


def _validate_and_normalize(data: dict, is_update=False):
    """Valida campos según límites y normaliza valores.
    Si is_update=True, los campos ausentes se mantienen como None (no serán aplicados).
    Devuelve un dict con campos normalizados o lanza ValueError con mensaje.
    """
    out = {}

    # nombre y apellido son requeridos en creación
    if not is_update:
        if not data.get('nombre'):
            raise ValueError('nombre es requerido')
        if not data.get('apellido'):
            raise ValueError('apellido es requerido')

    # Nombre
    if 'nombre' in data:
        nombre = data.get('nombre')
        if nombre is None or str(nombre).strip() == '':
            nombre = None
        else:
            nombre = _to_upper_str(nombre)
            if len(nombre) > NOMBRE_MAX:
                raise ValueError(f'nombre supera {NOMBRE_MAX} caracteres')
        out['nombre'] = nombre

    # Apellido
    if 'apellido' in data:
        apellido = data.get('apellido')
        if apellido is None or str(apellido).strip() == '':
            apellido = None
        else:
            apellido = _to_upper_str(apellido)
            if len(apellido) > APELLIDO_MAX:
                raise ValueError(f'apellido supera {APELLIDO_MAX} caracteres')
        out['apellido'] = apellido

    # Direccion
    if 'direccion' in data:
        direccion = data.get('direccion')
        if direccion is None or str(direccion).strip() == '':
            direccion = None
        else:
            direccion = _to_upper_str(direccion)
            if len(direccion) > DIRECCION_MAX:
                raise ValueError(f'direccion supera {DIRECCION_MAX} caracteres')
        out['direccion'] = direccion

    # Telefono
    if 'telefono' in data:
        telefono = data.get('telefono')
        if telefono is None or str(telefono).strip() == '':
            telefono = None
        else:
            telefono = _to_upper_str(telefono)
            if len(telefono) > TELEFONO_MAX:
                raise ValueError(f'telefono supera {TELEFONO_MAX} caracteres')
        out['telefono'] = telefono

    # Cedula: aceptar número o string de dígitos
    if 'cedula' in data:
        ced = data.get('cedula')
        if ced is None or (isinstance(ced, str) and ced.strip() == ''):
            cedula = None
        else:
            ced_str = str(ced).strip()
            if not ced_str.isdigit():
                raise ValueError('cedula debe ser numérica')
            if len(ced_str) > CEDULA_MAX:
                raise ValueError(f'cedula supera {CEDULA_MAX} dígitos')
            cedula = int(ced_str)
        out['cedula'] = cedula

    # Fecha de nacimiento: aceptar None, cadena ISO o date -> normalizar a date o None
    if 'fecha_nacimiento' in data:
        fn = data.get('fecha_nacimiento')
        if fn is None or (isinstance(fn, str) and fn.strip() == ''):
            fecha_nacimiento = None
        else:
            try:
                fecha_nacimiento = datetime.fromisoformat(fn).date() if isinstance(fn, str) else fn
            except Exception:
                raise ValueError('fecha_nacimiento inválida, usar YYYY-MM-DD o vacío')
        out['fecha_nacimiento'] = fecha_nacimiento

    return out

def get_all_alumnos():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_alumno, nombre, apellido, fecha_nacimiento, direccion, telefono, cedula, anu_alum FROM escuela.alumnos ORDER BY id_alumno ASC")
            rows = cur.fetchall()
            alumnos = []
            for r in rows:
                alumnos.append({
                    'id_alumno': r[0],
                    'nombre': r[1],
                    'apellido': r[2],
                    'fecha_nacimiento': r[3].isoformat() if r[3] else None,
                    'direccion': r[4],
                    'telefono': r[5],
                    'cedula': int(r[6]) if r[6] is not None else None,
                    'anu_alum': r[7]
                })
            return alumnos
    except Exception:
        raise

def get_alumno_by_id(id_alumno):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id_alumno, nombre, apellido, fecha_nacimiento, direccion, telefono, cedula, anu_alum FROM escuela.alumnos WHERE id_alumno = %s", (id_alumno,))
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id_alumno': r[0],
                'nombre': r[1],
                'apellido': r[2],
                'fecha_nacimiento': r[3].isoformat() if r[3] else None,
                'direccion': r[4],
                'telefono': r[5],
                'cedula': int(r[6]) if r[6] is not None else None,
                'anu_alum': r[7]
            }
    except Exception:
        raise

def create_alumno(data: dict):
    # Validar y normalizar entrada (lanza ValueError en caso de fallo)
    vals = _validate_and_normalize(data, is_update=False)

    nombre = vals.get('nombre')
    apellido = vals.get('apellido')
    direccion = vals.get('direccion')
    telefono = vals.get('telefono')
    cedula = vals.get('cedula')
    fecha_nacimiento = vals.get('fecha_nacimiento')

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO escuela.alumnos (nombre, apellido, fecha_nacimiento, direccion, telefono, cedula, anu_alum)
                VALUES (%s, %s, %s, %s, %s, %s, NULL)
                RETURNING id_alumno
                """,
                (nombre, apellido, fecha_nacimiento, direccion, telefono, cedula)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise

def update_alumno(id_alumno, data: dict):
    # Validar y normalizar los campos proporcionados (no requeridos)
    vals = _validate_and_normalize(data, is_update=True)

    nombre = vals.get('nombre') if 'nombre' in vals else None
    apellido = vals.get('apellido') if 'apellido' in vals else None
    direccion = vals.get('direccion') if 'direccion' in vals else None
    telefono = vals.get('telefono') if 'telefono' in vals else None
    cedula = vals.get('cedula') if 'cedula' in vals else None
    fecha_nacimiento = vals.get('fecha_nacimiento') if 'fecha_nacimiento' in vals else None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE escuela.alumnos
                SET nombre = COALESCE(%s, nombre),
                    apellido = COALESCE(%s, apellido),
                    fecha_nacimiento = COALESCE(%s, fecha_nacimiento),
                    direccion = COALESCE(%s, direccion),
                    telefono = COALESCE(%s, telefono),
                    cedula = COALESCE(%s, cedula)
                WHERE id_alumno = %s
                RETURNING id_alumno
                """,
                (nombre, apellido, fecha_nacimiento, direccion, telefono, cedula, id_alumno)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

def anular_alumno(id_alumno):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE escuela.alumnos SET anu_alum = 'X' WHERE id_alumno = %s RETURNING id_alumno", (id_alumno,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_alumno(id_alumno):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Dejar el campo NULL para indicar activo
            cur.execute("UPDATE escuela.alumnos SET anu_alum = NULL WHERE id_alumno = %s RETURNING id_alumno", (id_alumno,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

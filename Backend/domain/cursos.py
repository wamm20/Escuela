from domain.Configuration.database import get_db_connection
from datetime import datetime


def _to_upper_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    return value


# límites según la tabla cursos
NOMBRE_MAX = 255
ANIO_MAX = 50
ESTADO_MAX = 50


def _validate_and_normalize(data: dict, is_update=False):
    """Valida y normaliza datos de curso.
    En creación exige nombre_curso, anio_escolar, fecha_inicio y fecha_fin.
    Si is_update=True los campos pueden faltar y serán ignorados.
    Devuelve dict con valores o lanza ValueError.
    """
    out = {}

    if not is_update:
        for campo in ('nombre_curso', 'anio_escolar', 'fecha_inicio', 'fecha_fin'):
            if not data.get(campo):
                raise ValueError(f'{campo} es requerido')

    if 'nombre_curso' in data:
        nc = data.get('nombre_curso')
        if nc is None or str(nc).strip() == '':
            nc = None
        else:
            nc = _to_upper_str(nc)
            if len(nc) > NOMBRE_MAX:
                raise ValueError(f'nombre_curso supera {NOMBRE_MAX} caracteres')
        out['nombre_curso'] = nc

    if 'anio_escolar' in data:
        an = data.get('anio_escolar')
        if an is None or str(an).strip() == '':
            an = None
        else:
            an = _to_upper_str(an)
            if len(an) > ANIO_MAX:
                raise ValueError(f'anio_escolar supera {ANIO_MAX} caracteres')
        out['anio_escolar'] = an

    if 'estado_curso' in data:
        es = data.get('estado_curso')
        if es is None or str(es).strip() == '':
            es = None
        else:
            es = _to_upper_str(es)
            if len(es) > ESTADO_MAX:
                raise ValueError(f'estado_curso supera {ESTADO_MAX} caracteres')
        out['estado_curso'] = es

    if 'fecha_inicio' in data:
        fi = data.get('fecha_inicio')
        if fi is None or (isinstance(fi, str) and fi.strip() == ''):
            fecha_inicio = None
        else:
            try:
                fecha_inicio = datetime.fromisoformat(fi).date() if isinstance(fi, str) else fi
            except Exception:
                raise ValueError('fecha_inicio inválida, usar YYYY-MM-DD o vacío')
        out['fecha_inicio'] = fecha_inicio

    if 'fecha_fin' in data:
        ff = data.get('fecha_fin')
        if ff is None or (isinstance(ff, str) and ff.strip() == ''):
            fecha_fin = None
        else:
            try:
                fecha_fin = datetime.fromisoformat(ff).date() if isinstance(ff, str) else ff
            except Exception:
                raise ValueError('fecha_fin inválida, usar YYYY-MM-DD o vacío')
        out['fecha_fin'] = fecha_fin

    return out


# operaciones CRUD

def get_all_cursos():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_curso, nombre_curso, anio_escolar, fecha_inicio, fecha_fin, estado_curso, anu_cur "
                "FROM escuela.cursos ORDER BY id_curso ASC"
            )
            rows = cur.fetchall()
            cursos = []
            for r in rows:
                cursos.append({
                    'id_curso': r[0],
                    'nombre_curso': r[1],
                    'anio_escolar': r[2],
                    'fecha_inicio': r[3].isoformat() if r[3] else None,
                    'fecha_fin': r[4].isoformat() if r[4] else None,
                    'estado_curso': r[5],
                    'anu_cur': r[6]
                })
            return cursos
    except Exception:
        raise


def get_curso_by_id(id_curso):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_curso, nombre_curso, anio_escolar, fecha_inicio, fecha_fin, estado_curso, anu_cur "
                "FROM escuela.cursos WHERE id_curso = %s",
                (id_curso,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return {
                'id_curso': r[0],
                'nombre_curso': r[1],
                'anio_escolar': r[2],
                'fecha_inicio': r[3].isoformat() if r[3] else None,
                'fecha_fin': r[4].isoformat() if r[4] else None,
                'estado_curso': r[5],
                'anu_cur': r[6]
            }
    except Exception:
        raise


def create_curso(data: dict):
    vals = _validate_and_normalize(data, is_update=False)
    nombre = vals.get('nombre_curso')
    anio = vals.get('anio_escolar')
    fi = vals.get('fecha_inicio')
    ff = vals.get('fecha_fin')
    estado = vals.get('estado_curso')
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO escuela.cursos (nombre_curso, anio_escolar, fecha_inicio, fecha_fin, estado_curso, anu_cur)
                VALUES (%s, %s, %s, %s, COALESCE(%s, 'ABIERTO'), NULL)
                RETURNING id_curso
                """,
                (nombre, anio, fi, ff, estado)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise


def update_curso(id_curso, data: dict):
    vals = _validate_and_normalize(data, is_update=True)
    nombre = vals.get('nombre_curso') if 'nombre_curso' in vals else None
    anio = vals.get('anio_escolar') if 'anio_escolar' in vals else None
    fi = vals.get('fecha_inicio') if 'fecha_inicio' in vals else None
    ff = vals.get('fecha_fin') if 'fecha_fin' in vals else None
    estado = vals.get('estado_curso') if 'estado_curso' in vals else None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE escuela.cursos
                SET nombre_curso = COALESCE(%s, nombre_curso),
                    anio_escolar = COALESCE(%s, anio_escolar),
                    fecha_inicio = COALESCE(%s, fecha_inicio),
                    fecha_fin = COALESCE(%s, fecha_fin),
                    estado_curso = COALESCE(%s, estado_curso)
                WHERE id_curso = %s
                RETURNING id_curso
                """,
                (nombre, anio, fi, ff, estado, id_curso)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def anular_curso(id_curso):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE escuela.cursos SET anu_cur = 'X' WHERE id_curso = %s RETURNING id_curso", (id_curso,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_curso(id_curso):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE escuela.cursos SET anu_cur = NULL WHERE id_curso = %s RETURNING id_curso", (id_curso,))
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

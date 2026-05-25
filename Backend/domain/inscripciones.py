from domain.Configuration.database import get_db_connection


def _ensure_curso_exists(cur, id_curso):
    cur.execute("SELECT 1 FROM escuela.cursos WHERE id_curso = %s", (id_curso,))
    if not cur.fetchone():
        raise ValueError('curso no encontrado')


def _format_alumno_row(row):
    return {
        'id_alumno': row[0],
        'nombre': row[1],
        'apellido': row[2],
        'cedula': int(row[3]) if row[3] is not None else None,
    }


def get_alumnos_disponibles_por_curso(id_curso):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)
            cur.execute(
                """
                SELECT a.id_alumno, a.nombre, a.apellido, a.cedula
                FROM escuela.alumnos a
                WHERE a.anu_alum IS NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM escuela.inscripciones i
                      WHERE i.id_curso = %s
                        AND i.id_alumno = a.id_alumno
                  )
                ORDER BY a.apellido ASC, a.nombre ASC, a.id_alumno ASC
                """,
                (id_curso,)
            )
            return [_format_alumno_row(row) for row in cur.fetchall()]
    except Exception:
        raise


def get_inscripciones_por_curso(id_curso):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)
            cur.execute(
                """
                SELECT i.id_inscripcion,
                       i.id_alumno,
                       a.nombre,
                       a.apellido,
                       a.cedula,
                       i.fecha_inscripcion,
                       i.anu_alum
                FROM escuela.inscripciones i
                JOIN escuela.alumnos a ON a.id_alumno = i.id_alumno
                WHERE i.id_curso = %s
                ORDER BY (CASE WHEN i.anu_alum = 'X' THEN 1 ELSE 0 END), a.apellido ASC, a.nombre ASC, i.id_inscripcion ASC
                """,
                (id_curso,)
            )
            rows = cur.fetchall()
            inscripciones = []
            for row in rows:
                inscripciones.append({
                    'id_inscripcion': row[0],
                    'id_alumno': row[1],
                    'nombre': row[2],
                    'apellido': row[3],
                    'cedula': int(row[4]) if row[4] is not None else None,
                    'fecha_inscripcion': row[5].isoformat() if row[5] else None,
                    'anu_alum': row[6],
                })
            return inscripciones
    except Exception:
        raise


def add_inscripciones(id_curso, alumno_ids):
    if not alumno_ids:
        raise ValueError('debe seleccionar al menos un alumno')

    unique_ids = []
    seen = set()
    for alumno_id in alumno_ids:
        if alumno_id in seen:
            continue
        seen.add(alumno_id)
        unique_ids.append(alumno_id)

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)
            created_ids = []

            for alumno_id in unique_ids:
                cur.execute(
                    "SELECT 1 FROM escuela.alumnos WHERE id_alumno = %s AND anu_alum IS NULL",
                    (alumno_id,)
                )
                if not cur.fetchone():
                    raise ValueError(f'alumno {alumno_id} no encontrado o anulado')

                cur.execute(
                    "SELECT id_inscripcion FROM escuela.inscripciones WHERE id_curso = %s AND id_alumno = %s",
                    (id_curso, alumno_id)
                )
                existing = cur.fetchone()
                if existing:
                    raise ValueError(f'el alumno {alumno_id} ya pertenece o perteneció a este curso; use activar si está suspendido')

                cur.execute(
                    """
                    INSERT INTO escuela.inscripciones (id_alumno, id_curso, fecha_inscripcion, anu_alum)
                    VALUES (%s, %s, CURRENT_DATE, NULL)
                    RETURNING id_inscripcion
                    """,
                    (alumno_id, id_curso)
                )
                created_ids.append(cur.fetchone()[0])

            conn.commit()
            return created_ids
    except Exception:
        raise


def suspend_inscripciones(id_curso, inscripcion_ids):
    if not inscripcion_ids:
        raise ValueError('debe seleccionar al menos una inscripción')

    unique_ids = []
    seen = set()
    for inscripcion_id in inscripcion_ids:
        if inscripcion_id in seen:
            continue
        seen.add(inscripcion_id)
        unique_ids.append(inscripcion_id)

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)
            updated_ids = []

            for inscripcion_id in unique_ids:
                cur.execute(
                    "SELECT anu_alum FROM escuela.inscripciones WHERE id_inscripcion = %s AND id_curso = %s",
                    (inscripcion_id, id_curso)
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError(f'inscripción {inscripcion_id} no encontrada para este curso')
                if row[0] == 'X':
                    raise ValueError(f'inscripción {inscripcion_id} ya está suspendida')

                cur.execute(
                    "UPDATE escuela.inscripciones SET anu_alum = 'X' WHERE id_inscripcion = %s RETURNING id_inscripcion",
                    (inscripcion_id,)
                )
                updated_ids.append(cur.fetchone()[0])

            conn.commit()
            return updated_ids
    except Exception:
        raise


def activate_inscripciones(id_curso, inscripcion_ids):
    if not inscripcion_ids:
        raise ValueError('debe seleccionar al menos una inscripción')

    unique_ids = []
    seen = set()
    for inscripcion_id in inscripcion_ids:
        if inscripcion_id in seen:
            continue
        seen.add(inscripcion_id)
        unique_ids.append(inscripcion_id)

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)
            updated_ids = []

            for inscripcion_id in unique_ids:
                cur.execute(
                    "SELECT anu_alum FROM escuela.inscripciones WHERE id_inscripcion = %s AND id_curso = %s",
                    (inscripcion_id, id_curso)
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError(f'inscripción {inscripcion_id} no encontrada para este curso')
                if row[0] != 'X':
                    raise ValueError(f'inscripción {inscripcion_id} ya está activa')

                cur.execute(
                    "UPDATE escuela.inscripciones SET anu_alum = NULL WHERE id_inscripcion = %s RETURNING id_inscripcion",
                    (inscripcion_id,)
                )
                updated_ids.append(cur.fetchone()[0])

            conn.commit()
            return updated_ids
    except Exception:
        raise
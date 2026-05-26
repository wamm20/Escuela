from datetime import date, datetime
import re

from domain.Configuration.database import get_db_connection


MIN_NOTA = 1
MAX_NOTA = 20
NOTA_PATTERN = re.compile(r'^\d{1,2}(\.\d{1,2})?$')


def _parse_nota(value):
    raw_value = '' if value is None else str(value).strip()
    if raw_value == '':
        raise ValueError('nota es requerida')

    if not NOTA_PATTERN.match(raw_value):
        raise ValueError('nota inválida, usar hasta 2 enteros y 2 decimales')

    try:
        nota = float(raw_value)
    except (TypeError, ValueError):
        raise ValueError('nota inválida')

    if nota < MIN_NOTA or nota > MAX_NOTA:
        raise ValueError(f'nota fuera de rango ({MIN_NOTA}-{MAX_NOTA})')
    return round(nota, 2)


def _parse_fecha(value):
    if value is None or str(value).strip() == '':
        return date.today()
    if isinstance(value, date):
        parsed_date = value
    else:
        try:
            parsed_date = datetime.fromisoformat(str(value)).date()
        except ValueError:
            raise ValueError('fecha_calificacion inválida, usar YYYY-MM-DD')

    if parsed_date > date.today():
        raise ValueError('fecha_calificacion no puede ser mayor a la fecha actual')

    return parsed_date


def _ensure_curso_exists(cur, id_curso):
    cur.execute('SELECT 1 FROM escuela.cursos WHERE id_curso = %s', (id_curso,))
    if not cur.fetchone():
        raise ValueError('curso no encontrado')


def _get_active_inscripcion(cur, id_curso, id_inscripcion):
    cur.execute(
        """
        SELECT i.id_inscripcion,
               i.id_alumno,
               a.nombre,
               a.apellido,
               a.cedula
        FROM escuela.inscripciones i
        JOIN escuela.alumnos a ON a.id_alumno = i.id_alumno
        WHERE i.id_curso = %s
          AND i.id_inscripcion = %s
          AND COALESCE(i.anu_alum, '') <> 'X'
        """,
        (id_curso, id_inscripcion),
    )
    return cur.fetchone()


def _get_active_curso_materia(cur, id_curso, id_curso_materia):
    cur.execute(
        """
        SELECT cm.id_curso_materia,
               cm.id_materia,
               m.nombre_materia,
               cm.id_profesor,
               p.nombre,
               p.apellido
        FROM escuela.curso_materia cm
        JOIN escuela.materias m ON m.id_materia = cm.id_materia
        LEFT JOIN escuela.profesores p ON p.id_profesor = cm.id_profesor
        WHERE cm.id_curso = %s
          AND cm.id_curso_materia = %s
          AND COALESCE(cm.anu_cur_mat, '') <> 'X'
        """,
        (id_curso, id_curso_materia),
    )
    return cur.fetchone()


def get_estado_calificaciones_por_curso(id_curso):
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
                       i.fecha_inscripcion
                FROM escuela.inscripciones i
                JOIN escuela.alumnos a ON a.id_alumno = i.id_alumno
                WHERE i.id_curso = %s
                  AND COALESCE(i.anu_alum, '') <> 'X'
                ORDER BY a.apellido ASC, a.nombre ASC, i.id_inscripcion ASC
                """,
                (id_curso,),
            )
            alumnos = [
                {
                    'id_inscripcion': row[0],
                    'id_alumno': row[1],
                    'nombre': row[2],
                    'apellido': row[3],
                    'cedula': int(row[4]) if row[4] is not None else None,
                    'fecha_inscripcion': row[5].isoformat() if row[5] else None,
                }
                for row in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT cm.id_curso_materia,
                       cm.id_materia,
                       m.nombre_materia,
                       cm.id_profesor,
                       p.nombre,
                       p.apellido
                FROM escuela.curso_materia cm
                JOIN escuela.materias m ON m.id_materia = cm.id_materia
                LEFT JOIN escuela.profesores p ON p.id_profesor = cm.id_profesor
                WHERE cm.id_curso = %s
                  AND COALESCE(cm.anu_cur_mat, '') <> 'X'
                ORDER BY m.nombre_materia ASC, cm.id_curso_materia ASC
                """,
                (id_curso,),
            )
            materias = [
                {
                    'id_curso_materia': row[0],
                    'id_materia': row[1],
                    'nombre_materia': row[2],
                    'id_profesor': row[3],
                    'nombre_profesor': f"{row[4]} {row[5]}" if row[4] and row[5] else None,
                }
                for row in cur.fetchall()
            ]

            cur.execute(
                """
                SELECT c.id_calificacion,
                       c.id_inscripcion,
                       c.id_curso_materia,
                       c.nota,
                       c.fecha_calificacion,
                       a.nombre,
                       a.apellido,
                       m.nombre_materia
                FROM escuela.calificaciones c
                JOIN escuela.inscripciones i ON i.id_inscripcion = c.id_inscripcion
                JOIN escuela.alumnos a ON a.id_alumno = i.id_alumno
                JOIN escuela.curso_materia cm ON cm.id_curso_materia = c.id_curso_materia
                JOIN escuela.materias m ON m.id_materia = cm.id_materia
                WHERE i.id_curso = %s
                ORDER BY a.apellido ASC, a.nombre ASC, m.nombre_materia ASC, c.id_calificacion ASC
                """,
                (id_curso,),
            )
            calificaciones = [
                {
                    'id_calificacion': row[0],
                    'id_inscripcion': row[1],
                    'id_curso_materia': row[2],
                    'nota': float(row[3]),
                    'fecha_calificacion': row[4].isoformat() if row[4] else None,
                    'nombre': row[5],
                    'apellido': row[6],
                    'nombre_materia': row[7],
                }
                for row in cur.fetchall()
            ]

            return {
                'alumnos': alumnos,
                'materias': materias,
                'calificaciones': calificaciones,
            }
    except Exception:
        raise


def save_calificacion(data):
    id_curso = data.get('id_curso')
    id_inscripcion = data.get('id_inscripcion')
    id_curso_materia = data.get('id_curso_materia')
    id_calificacion = data.get('id_calificacion')

    if not id_curso:
        raise ValueError('id_curso es requerido')
    if not id_inscripcion:
        raise ValueError('id_inscripcion es requerido')
    if not id_curso_materia:
        raise ValueError('id_curso_materia es requerido')

    nota = _parse_nota(data.get('nota'))
    fecha_calificacion = _parse_fecha(data.get('fecha_calificacion'))

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            _ensure_curso_exists(cur, id_curso)

            inscripcion = _get_active_inscripcion(cur, id_curso, id_inscripcion)
            if not inscripcion:
                raise ValueError('la inscripción no pertenece al curso o está bloqueada')
            id_alumno = inscripcion[1]

            curso_materia = _get_active_curso_materia(cur, id_curso, id_curso_materia)
            if not curso_materia:
                raise ValueError('la materia no pertenece al curso o está anulada')

            existing = None
            if id_calificacion:
                cur.execute(
                    'SELECT id_calificacion FROM escuela.calificaciones WHERE id_calificacion = %s',
                    (id_calificacion,),
                )
                existing = cur.fetchone()
            else:
                cur.execute(
                    """
                    SELECT id_calificacion
                    FROM escuela.calificaciones
                    WHERE id_inscripcion = %s AND id_curso_materia = %s
                    """,
                    (id_inscripcion, id_curso_materia),
                )
                existing = cur.fetchone()

            if existing:
                resolved_id = existing[0]
                cur.execute(
                    """
                    UPDATE escuela.calificaciones
                    SET id_inscripcion = %s,
                        id_alumno = %s,
                        id_curso_materia = %s,
                        nota = %s,
                        fecha_calificacion = %s
                    WHERE id_calificacion = %s
                    RETURNING id_calificacion
                    """,
                    (id_inscripcion, id_alumno, id_curso_materia, nota, fecha_calificacion, resolved_id),
                )
                result_id = cur.fetchone()[0]
                action = 'updated'
            else:
                cur.execute(
                    """
                    INSERT INTO escuela.calificaciones (id_inscripcion, id_alumno, id_curso_materia, nota, fecha_calificacion)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_calificacion
                    """,
                    (id_inscripcion, id_alumno, id_curso_materia, nota, fecha_calificacion),
                )
                result_id = cur.fetchone()[0]
                action = 'created'

            conn.commit()
            return {
                'id_calificacion': result_id,
                'action': action,
            }
    except Exception:
        raise
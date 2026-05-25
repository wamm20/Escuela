from domain.Configuration.database import get_db_connection



def get_materias_por_curso(id_curso):
    """Devuelve la lista de asignaciones de materia/profesor para un curso."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT cm.id_curso_materia,
                       cm.id_materia,
                       m.nombre_materia,
                       cm.id_profesor,
                       p.nombre as prof_nombre,
                       p.apellido as prof_apellido,
                       cm.anu_cur_mat
                FROM escuela.curso_materia cm
                JOIN escuela.materias m ON m.id_materia = cm.id_materia
                LEFT JOIN escuela.profesores p ON p.id_profesor = cm.id_profesor
                WHERE cm.id_curso = %s
                ORDER BY cm.id_curso_materia ASC
                """,
                (id_curso,)
            )
            rows = cur.fetchall()
            results = []
            for r in rows:
                results.append({
                    'id_curso_materia': r[0],
                    'id_materia': r[1],
                    'nombre_materia': r[2],
                    'id_profesor': r[3],
                    'nombre_profesor': f"{r[4]} {r[5]}" if r[4] and r[5] else None,
                    'anu_cur_mat': r[6]
                })
            return results
    except Exception:
        raise


def add_or_update_asignacion(id_curso, id_materia, id_profesor):
    """Inserta una nueva fila o actualiza el profesor si ya existía la materia en el curso.
    Devuelve el id_curso_materia que fue creado/actualizado.
    Lanza ValueError si alguno de los identificadores no es válido.
    """
    if not id_curso or not id_materia or not id_profesor:
        raise ValueError('curso, materia y profesor son requeridos')

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Validar existencia de curso, materia y profesor
            cur.execute("SELECT 1 FROM escuela.cursos WHERE id_curso = %s", (id_curso,))
            if not cur.fetchone():
                raise ValueError('curso no encontrado')
            cur.execute("SELECT 1 FROM escuela.materias WHERE id_materia = %s", (id_materia,))
            if not cur.fetchone():
                raise ValueError('materia no encontrada')
            cur.execute("SELECT 1 FROM escuela.profesores WHERE id_profesor = %s", (id_profesor,))
            if not cur.fetchone():
                raise ValueError('profesor no encontrado')

            cur.execute(
                "SELECT id_curso_materia FROM escuela.curso_materia WHERE id_curso = %s AND id_materia = %s",
                (id_curso, id_materia)
            )
            existing = cur.fetchone()
            if existing:
                # update profesor
                cur.execute(
                    "UPDATE escuela.curso_materia SET id_profesor = %s WHERE id_curso_materia = %s RETURNING id_curso_materia",
                    (id_profesor, existing[0])
                )
                new_id = cur.fetchone()[0]
            else:
                cur.execute(
                    "INSERT INTO escuela.curso_materia (id_curso, id_materia, id_profesor) VALUES (%s, %s, %s) RETURNING id_curso_materia",
                    (id_curso, id_materia, id_profesor)
                )
                new_id = cur.fetchone()[0]
            conn.commit()
            return new_id
    except Exception:
        raise


def anular_asignacion(id_curso_materia):
    """Marca la fila como anulada (anu_cur_mat='X')."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.curso_materia SET anu_cur_mat = 'X' WHERE id_curso_materia = %s RETURNING id_curso_materia",
                (id_curso_materia,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise


def activar_asignacion(id_curso_materia):
    """Quita el flag de anulación (anu_cur_mat=NULL)."""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE escuela.curso_materia SET anu_cur_mat = NULL WHERE id_curso_materia = %s RETURNING id_curso_materia",
                (id_curso_materia,)
            )
            res = cur.fetchone()
            if not res:
                return None
            conn.commit()
            return res[0]
    except Exception:
        raise

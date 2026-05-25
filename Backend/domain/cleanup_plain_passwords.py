"""Respalda y limpia las contraseñas en texto plano de `escuela.usuarios` (dominio).

Se mantiene la funcionalidad original y ahora forma parte del paquete `domain`.
"""
import argparse
from domain.Configuration.database import get_db_connection


def cleanup(dry_run: bool = False):
    with get_db_connection() as conn:
        if not conn:
            print('ERROR: no db connection')
            return 1
        cur = conn.cursor()
        # Crear tabla de backup
        cur.execute('''
            CREATE TABLE IF NOT EXISTS escuela.usuarios_pwr_plain_backup (
                id_usuario integer,
                usuario text,
                pwr_usuario_plain text,
                backed_at timestamptz DEFAULT now()
            )
        ''')
        # Contar filas a respaldar
        cur.execute("SELECT COUNT(*) FROM escuela.usuarios WHERE pwr_usuario_plain IS NOT NULL")
        count = cur.fetchone()[0]
        print(f"Filas con pwr_usuario_plain a respaldar: {count}")

        if count == 0:
            print('Nada que limpiar.')
            return 0

        if dry_run:
            print('Dry-run: no se harán cambios.')
            return 0

        # Insertar en backup
        cur.execute("INSERT INTO escuela.usuarios_pwr_plain_backup (id_usuario, usuario, pwr_usuario_plain) SELECT id_usuario, usuario, pwr_usuario_plain FROM escuela.usuarios WHERE pwr_usuario_plain IS NOT NULL")
        # Limpiar columna
        cur.execute("UPDATE escuela.usuarios SET pwr_usuario_plain = NULL WHERE pwr_usuario_plain IS NOT NULL")
        conn.commit()
        print(f"Respaldo realizado y {count} filas limpiadas.")
        cur.close()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-run', action='store_true', help='Dry-run: no hace cambios')
    args = parser.parse_args()
    exit(cleanup(dry_run=args.no_run))

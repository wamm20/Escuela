"""Migra contraseñas en `escuela.usuarios` a bcrypt (capa de aplicaciones).

Este script implementa la regla de negocio de migración y ahora forma parte
de la capa `applications`.
"""
import argparse
from domain.Configuration.database import get_db_connection
import bcrypt


def ensure_columns(cur):
    cur.execute("ALTER TABLE escuela.usuarios ADD COLUMN IF NOT EXISTS pwr_usuario_plain text;")
    cur.execute("ALTER TABLE escuela.usuarios ADD COLUMN IF NOT EXISTS pwr_usuario_hash text;")


def migrate(dry_run: bool = False):
    with get_db_connection() as conn:
        if not conn:
            print('No se pudo conectar a la base de datos')
            return
        cur = conn.cursor()
        ensure_columns(cur)
        conn.commit()

        # Selecciona usuarios que aún no tengan hash
        cur.execute("SELECT id_usuario, usuario, pwr_usuario FROM escuela.usuarios WHERE pwr_usuario_hash IS NULL")
        rows = cur.fetchall()
        print(f"Usuarios a procesar: {len(rows)}")

        for user_id, usuario, pwr in rows:
            if pwr is None:
                print(f"- Usuario {usuario} (id {user_id}) tiene pwr_usuario NULL, se omite")
                continue

            pwr_str = pwr.decode('utf-8') if isinstance(pwr, (bytes, bytearray)) else str(pwr)

            # Si ya parece un hash bcrypt, lo copiamos a pwr_usuario_hash
            if pwr_str.startswith('$2a$') or pwr_str.startswith('$2b$') or pwr_str.startswith('$2y$'):
                print(f"- Usuario {usuario} (id {user_id}) ya tiene formato bcrypt; copiando a pwr_usuario_hash")
                if not dry_run:
                    cur.execute("UPDATE escuela.usuarios SET pwr_usuario_hash = %s WHERE id_usuario = %s", (pwr_str, user_id))
                continue

            # Generar hash bcrypt
            hashed = bcrypt.hashpw(pwr_str.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            print(f"- Usuario {usuario} (id {user_id}) -> hash creado")
            if not dry_run:
                # Guarda el texto original en pwr_usuario_plain si está vacío
                cur.execute("UPDATE escuela.usuarios SET pwr_usuario_plain = COALESCE(pwr_usuario_plain, %s), pwr_usuario_hash = %s WHERE id_usuario = %s",
                            (pwr_str, hashed, user_id))

        if not dry_run:
            conn.commit()
            print('Migración completada y cambios confirmados en la base de datos.')
        else:
            print('Dry-run completado. No se hicieron cambios.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migra pwr_usuario a bcrypt')
    parser.add_argument('--dry-run', action='store_true', help='No realiza cambios en la BD, solo muestra acciones')
    args = parser.parse_args()
    migrate(dry_run=args.dry_run)

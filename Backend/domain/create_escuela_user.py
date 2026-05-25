"""Script que crea usuarios en la tabla `escuela.usuarios` (dominio).

Se mantiene la funcionalidad original pero ahora forma parte del paquete `domain`.
"""
import sys
from domain.Configuration.database import get_db_connection
import bcrypt


def create_user(nom_usuario, ape_usuario, password, ci_usuario=0, nvl_usuario=1, cargo=''):
    with get_db_connection() as conn:
        if not conn:
            print('No se pudo conectar a la base de datos')
            return
        cur = conn.cursor()
        # Aseguramos columnas auxiliares para hashes
        cur.execute("ALTER TABLE escuela.usuarios ADD COLUMN IF NOT EXISTS pwr_usuario_plain text;")
        cur.execute("ALTER TABLE escuela.usuarios ADD COLUMN IF NOT EXISTS pwr_usuario_hash text;")

        # Generar hash
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Determinar id_usuario (buscar max y sumar 1)
        cur.execute("SELECT COALESCE(MAX(id_usuario), 0) + 1 FROM escuela.usuarios")
        new_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO escuela.usuarios (id_usuario, ci_usuario, nom_usuario, ape_usuario, pwr_usuario, nvl_usuario, cargo_usuario, pwr_usuario_plain, pwr_usuario_hash) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (new_id, ci_usuario, nom_usuario, ape_usuario, None, nvl_usuario, cargo, password, hashed)
        )
        conn.commit()
        cur.close()
        print(f"Usuario creado con id_usuario={new_id}")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Uso: python create_escuela_user.py <nom_usuario> <ape_usuario> <password> [ci_usuario] [nvl_usuario] [cargo]')
    else:
        ci = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        nvl = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        cargo = sys.argv[6] if len(sys.argv) > 6 else ''
        create_user(sys.argv[1], sys.argv[2], sys.argv[3], ci_usuario=ci, nvl_usuario=nvl, cargo=cargo)

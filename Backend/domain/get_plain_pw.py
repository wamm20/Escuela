import sys
from domain.Configuration.database import get_db_connection

def get_plain(username):
    with get_db_connection() as conn:
        if not conn:
            print('ERROR: no db connection')
            return 1
        cur = conn.cursor()
        cur.execute("SELECT pwr_usuario_plain, pwr_usuario FROM escuela.usuarios WHERE usuario = %s", (username,))
        r = cur.fetchone()
        cur.close()
        if not r:
            print('NOT FOUND')
            return 2
        plain, orig = r
        print(plain if plain is not None else (orig if orig is not None else ''))
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python get_plain_pw.py <username>')
        sys.exit(3)
    sys.exit(get_plain(sys.argv[1]))

"""Utilidad para crear una tabla `users` y un usuario inicial (dominio)."""
from domain.Configuration.database import get_db_connection
import bcrypt
import sys


def create_user(username: str, password: str):
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with get_db_connection() as conn:
        if not conn:
            print("No se pudo conectar a la base de datos.")
            return
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash BYTEA NOT NULL
        );""")
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
            (username, pw_hash),
        )
        conn.commit()
        cur.close()
        print(f"Usuario '{username}' creado (o ya existía).")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python create_user.py <username> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])

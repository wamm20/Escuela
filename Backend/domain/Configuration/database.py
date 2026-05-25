import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
import logging
from contextlib import contextmanager

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Recoge las credenciales y valida que todas existan
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT")

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]):
    logging.error("Faltan una o más variables de entorno de la base de datos (DB_HOST, DB_NAME, etc.).")

def connect_to_db():
    """
    Establece una conexión con la base de datos PostgreSQL y la devuelve.
    """
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT]):
        return None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        # Asegurar codificación cliente en UTF8 para evitar problemas con acentos
        try:
            conn.set_client_encoding('UTF8')
        except Exception:
            pass
        logging.info("¡Conexión a la base de datos PostgreSQL exitosa!")
        return conn
    except OperationalError as e:
        logging.error(f"No se pudo conectar a la base de datos: {e}")
        return None

@contextmanager
def get_db_connection():
    """Generador de contexto para manejar la conexión a la BD."""
    conn = connect_to_db()
    try:
        yield conn
    finally:
        if conn:
            conn.close()
            logging.info("La conexión ha sido cerrada.")

if __name__ == '__main__':
    logging.info("Probando la conexión a la base de datos usando el gestor de contexto...")
    with get_db_connection() as conn:
        if conn:
            logging.info("La conexión se estableció y se cerrará automáticamente.")
        else:
            logging.warning("No se pudo establecer la conexión.")

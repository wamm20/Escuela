from flask import Flask
from dotenv import load_dotenv
import os

# Carga variables de entorno
load_dotenv()

app = Flask(__name__)

# Registro de blueprints de rutas (relativo dentro del paquete infrastructure)
try:
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.alumnos import alumnos_bp
    from .routes.profesores import profesores_bp
    from .routes.materias import materias_bp
    from .routes.cursos import cursos_bp
    from .routes.programas import programas_bp
    from .routes.inscripciones import inscripciones_bp
    from .routes.calificaciones import calificaciones_bp
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(alumnos_bp, url_prefix='/api')
    app.register_blueprint(profesores_bp, url_prefix='/api')
    app.register_blueprint(materias_bp, url_prefix='/api')
    app.register_blueprint(cursos_bp, url_prefix='/api')
    app.register_blueprint(programas_bp, url_prefix='/api')
    app.register_blueprint(inscripciones_bp, url_prefix='/api')
    app.register_blueprint(calificaciones_bp, url_prefix='/api')
except Exception as e:
    # Si las rutas faltan, dejamos que el import falle para visibilidad
    app.logger.warning(f"No se pudo cargar un blueprint: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

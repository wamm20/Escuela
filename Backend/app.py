from dotenv import load_dotenv
import os
from importlib import import_module

# Carga variables de entorno
load_dotenv()

# Importar la app desde la capa de infraestructura
infra = import_module('infrastructure.app')
app = getattr(infra, 'app')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

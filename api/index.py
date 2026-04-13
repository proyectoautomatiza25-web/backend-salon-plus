import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# CARGAR CONFIGURACIÓN REAL ANTES DE IMPORTAR APP
from app.config_loader import apply_config
apply_config()

from app.main import app

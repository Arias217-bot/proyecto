from routes.entidad_routes import EntidadRoutes

# Modelos
from models.equipo import Equipo

# Blueprints
equipo_routes = EntidadRoutes('equipo', Equipo)
equipo_bp = equipo_routes.bp  # El Blueprint que usaremos en `app.py`

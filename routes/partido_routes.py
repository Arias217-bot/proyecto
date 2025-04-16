# routes/partido_routes.py
from routes.entidad_routes import EntidadRoutes
from models.partido import Partido

from flask import render_template
from config import db

# Blueprints
partido_routes = EntidadRoutes('partido', Partido)
partido_bp = partido_routes.bp  # El Blueprint que usaremos en `app.py`

@partido_bp.route('/ver/<int:id_partido>')
def partido_page(id_partido):
    partido = db.session.get(Partido, id_partido)
    if not partido:
        return "Partido no encontrado", 404
    return render_template('partido.html', partido=partido, id_partido=id_partido)

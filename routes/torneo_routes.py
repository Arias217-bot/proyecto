# routes/torneo_routes.py
from routes.entidad_routes import EntidadRoutes
from models.torneo import Torneo

from flask import render_template, request
from config import db

# Blueprints
torneo_routes = EntidadRoutes('torneo', Torneo)
torneo_bp = torneo_routes.bp
torneo_bp.name = "torneo"  # El Blueprint que usaremos en `app.py`

@torneo_bp.route('/ver', endpoint='torneo_page')
def torneo_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        torneos = db.session.query(Torneo).filter(
            Torneo.nombre_torneo.ilike(f"%{query}%")
        ).all()
    else:
        torneos = db.session.query(Torneo).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('torneo.html', torneos=torneos, q=query)
# routes/equipo_rival_routes.py
from routes.entidad_routes import EntidadRoutes
from models.equipo_rival import EquipoRival

from flask import render_template, request
from config import db

# Blueprints
equipo_rival_routes = EntidadRoutes('equipo_rival', EquipoRival)
equipo_rival_bp = equipo_rival_routes.bp
equipo_rival_bp.name = "equipo_rival"  # El Blueprint que usaremos en `app.py`

@equipo_rival_bp.route('/ver', endpoint='equipo_rival_page')
def equipo_rival_page():
    # Obtener el parámetro de búsqueda
    query = request.args.get('q', '')
    if query:
        # Filtrar por nombre (busqueda insensible a mayúsculas)
        equipos_rivales = db.session.query(EquipoRival).filter(
            EquipoRival.nombre_equipo_rival.ilike(f"%{query}%")
        ).all()
    else:
        equipos_rivales = db.session.query(EquipoRival).all()
    # Pasar el valor de búsqueda a la plantilla
    return render_template('equipo_rival.html', equipos_rivales=equipos_rivales, q=query)
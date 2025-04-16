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

@torneo_bp.route('/<nombre_equipo>/<nombre_torneo>', endpoint='torneo_detalle')
def detalle_torneo(nombre_equipo, nombre_torneo):
    # Formatea los nombres (como haces en la ruta de equipo)
    nombre_equipo_formateado = nombre_equipo.replace("-", " ").lower()
    nombre_torneo_formateado = nombre_torneo.replace("-", " ").lower()
    
    # Buscar el equipo por nombre (asumiendo nombre único)
    equipo = db.session.query(Torneo.equipo.property.mapper.class_).filter(
        db.func.lower(Torneo.equipo.property.mapper.class_.nombre) == nombre_equipo_formateado
    ).first()

    if not equipo:
        return "Equipo no encontrado", 404

    # Buscar torneo por nombre y por equipo
    torneo = db.session.query(Torneo).filter(
        db.func.lower(Torneo.nombre_torneo) == nombre_torneo_formateado,
        Torneo.id_equipo == equipo.id_equipo
    ).first()

    if not torneo:
        return "Torneo no encontrado", 404

    return render_template('detalle_torneo.html', torneo=torneo, equipo=equipo)

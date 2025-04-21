# routes/partido_routes.py
from routes.entidad_routes import EntidadRoutes
from flask import render_template, request
from config import db
# Modelos
from models.partido import Partido

# Blueprints
partido_routes = EntidadRoutes('partido', Partido)
partido_bp = partido_routes.bp  # El Blueprint que usaremos en `app.py`

@partido_bp.route('/partido', methods=['GET'])
def partido():

    query = request.args.get('q','')
    if query:
        partidos_lista = db.session.query(Partido).filter(
            Partido.id_partido.like(f'%{query}%') 
        ).all()
    else:
        partidos_lista = db.session.query(Partido).all()
    return render_template('partido.html', partidos=partidos_lista,q=query)
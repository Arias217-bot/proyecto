# routes/usuario_routes.py
from routes.entidad_routes import EntidadRoutes

from models.usuario import Usuario
from models.equipo import Equipo
from models.categoria_edad import CategoriaEdad
from models.categoria_sexo import CategoriaSexo
from models.usuario_equipo import Usuario_Equipo

from flask import render_template
from config import db

# Blueprints
equipo_routes = EntidadRoutes('equipo', Equipo)
equipo_bp = equipo_routes.bp  # El Blueprint que usaremos en `app.py`

@equipo_bp.route('/ver/<documento>')
def perfil_equipos(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    # Obtener los equipos en los que el usuario está registrado en la tabla intermedia
    equipos = (
        db.session.query(Equipo)
        .join(Usuario_Equipo, Usuario_Equipo.id_equipo == Equipo.id_equipo)
        .filter(Usuario_Equipo.documento == documento)
        .all()
    )

    categorias_edad = CategoriaEdad.query.all()
    categorias_sexo = CategoriaSexo.query.all()

    return render_template(
        'equipos.html',
        usuario=usuario,
        equipos=[e.to_dict() for e in equipos],  # Solo equipos donde está el usuario
        categorias_edad=categorias_edad,
        categorias_sexo=categorias_sexo,
        documento=documento
    )

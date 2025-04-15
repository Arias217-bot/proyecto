# routes/usuario_routes.py
from routes.entidad_routes import EntidadRoutes

from models.usuario import Usuario
from models.equipo import Equipo
from models.rol import Rol
from models.posicion import Posicion
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

@equipo_bp.route('/<documento>/<nombre_equipo>')
def detalle_equipo(documento, nombre_equipo):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    # Obtener todos los equipos del usuario
    equipos = (
        db.session.query(Equipo)
        .join(Usuario_Equipo, Usuario_Equipo.id_equipo == Equipo.id_equipo)
        .filter(Usuario_Equipo.documento == documento)
        .all()
    )

    # Buscar por nombre formateado
    equipo = next(
        (e for e in equipos if e.nombre.replace(" ", "-").lower() == nombre_equipo),
        None
    )
    if not equipo:
        return "Equipo no encontrado", 404

    # Obtener categorías
    categoria_edad = db.session.get(CategoriaEdad, equipo.id_categoria_edad)
    categoria_sexo = db.session.get(CategoriaSexo, equipo.id_categoria_sexo)

    # Obtener integrantes
    integrantes = (
        db.session.query(Usuario, Rol, Posicion)
        .join(Usuario_Equipo, Usuario.documento == Usuario_Equipo.documento)
        .outerjoin(Rol, Usuario_Equipo.id_rol == Rol.id_rol)
        .outerjoin(Posicion, Usuario_Equipo.id_posicion == Posicion.id_posicion)
        .filter(Usuario_Equipo.id_equipo == equipo.id_equipo)
        .all()
    )

    integrantes_lista = [
        {
            "documento": usuario.documento,
            "nombre": usuario.nombre,
            "rol": rol.nombre if rol else "Sin rol",
            "posicion": posicion.nombre if posicion else "Sin posición"
        }
        for usuario, rol, posicion in integrantes
    ]

    equipo_detalle = {
        "nombre": equipo.nombre,
        "descripcion": equipo.descripcion,
        "categoria_edad": categoria_edad.nombre if categoria_edad else "Sin categoría",
        "categoria_sexo": categoria_sexo.nombre if categoria_sexo else "Sin categoría"
    }

    return render_template(
        'detalle_equipo.html',
        usuario=usuario,
        equipo=equipo_detalle,
        integrantes=integrantes_lista,
        documento=documento
    )

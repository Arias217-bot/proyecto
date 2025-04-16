# routes/equipo_routes.py
from routes.entidad_routes import EntidadRoutes

from models.usuario import Usuario
from models.equipo import Equipo
from models.rol import Rol
from models.posicion import Posicion
from models.categoria_edad import CategoriaEdad
from models.categoria_sexo import CategoriaSexo
from models.usuario_equipo import Usuario_Equipo
from models.mensajes import Mensajes
from models.torneo import Torneo

from flask import render_template, request, jsonify
from config import db

# Blueprints
equipo_routes = EntidadRoutes('equipo', Equipo)
equipo_bp = equipo_routes.bp  # El Blueprint que usaremos en `app.py`

@equipo_bp.route('/ver/<documento>')
def perfil_equipos(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    equipos = (db.session.query(Equipo)
                .join(Usuario_Equipo, Usuario_Equipo.id_equipo == Equipo.id_equipo)
                .filter(Usuario_Equipo.documento == documento)
                .all())

    categorias_edad = CategoriaEdad.query.all()
    categorias_sexo = CategoriaSexo.query.all()

    return render_template(
        'equipos.html',
        usuario=usuario,
        equipos=[e.to_dict() for e in equipos],
        categorias_edad=categorias_edad,
        categorias_sexo=categorias_sexo,
        documento=documento
    )

@equipo_bp.route('/<documento>/<nombre_equipo>')
def detalle_equipo(documento, nombre_equipo):

    # Obtener usuario
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
        db.session.query(Usuario, Rol, Posicion, Usuario_Equipo.numero)
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
            "posicion": posicion.nombre if posicion else "Sin posición",
            "numero": numero
        }
        for usuario, rol, posicion, numero in integrantes
    ]

    # Verificar mensajes con autor
    mensajes = (
        db.session.query(Mensajes, Usuario)
        .join(Usuario, Mensajes.autor == Usuario.documento)
        .filter(Mensajes.id_equipo == equipo.id_equipo)
        .order_by(Mensajes.fecha_envio.asc())
        .all()
    )

    mensajes_lista = [
        {
            "id_mensaje": mensaje.id_mensaje,
            "contenido": mensaje.contenido,
            "fecha_envio": mensaje.fecha_envio.strftime("%Y-%m-%d %H:%M:%S"),
            "autor": usuario.nombre
        }
        for mensaje, usuario in mensajes
    ]

    # Obtener torneos del equipo
    torneos = (
        db.session.query(Torneo)
        .filter(Torneo.id_equipo == equipo.id_equipo)
        .all()
    )

    torneos_lista = [
        {
            "id_torneo": torneo.id_torneo,
            "nombre_torneo": torneo.nombre_torneo,
            "descripcion": torneo.descripcion
        }
        for torneo in torneos
    ]

    # Obtener roles y posiciones
    roles = Rol.query.all()
    posiciones = Posicion.query.all()

    equipo_detalle = {
        "id_equipo": equipo.id_equipo,
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
        roles=roles,
        posiciones=posiciones,
        documento=documento,
        mensajes=mensajes_lista,
        torneos=torneos_lista,
    )

@equipo_bp.route('/integrantes/crear', methods=['POST'])
def crear_integrante():
    data = request.json
    documento = data.get('documento')
    id_rol = data.get('rol')
    id_posicion = data.get('posicion')
    id_equipo = data.get('id_equipo')
    numero = data.get('numero')  # Se obtiene el valor de número desde el JSON

    nuevo_integrante = Usuario_Equipo(
        documento=documento,
        id_equipo=id_equipo,
        id_rol=id_rol,
        id_posicion=id_posicion,
        numero=numero  # Se utiliza el valor digitado en la solicitud
    )
    db.session.add(nuevo_integrante)
    db.session.commit()

    return jsonify({"mensaje": "Integrante creado exitosamente"}), 201

@equipo_bp.route('/integrantes/editar', methods=['POST'])
def editar_integrante():
    data = request.json
    documento = data.get('documento')
    id_equipo = data.get('id_equipo')
    id_rol = data.get('rol')
    id_posicion = data.get('posicion')
    numero = data.get('numero')

    integrante = Usuario_Equipo.query.filter_by(documento=documento, id_equipo=id_equipo).first()
    if not integrante:
        return jsonify({"error": "Integrante no encontrado"}), 404

    integrante.id_rol = id_rol
    integrante.id_posicion = id_posicion
    integrante.numero = numero
    db.session.commit()

    return jsonify({"mensaje": "Integrante actualizado correctamente"}), 200

@equipo_bp.route('/integrantes/borrar', methods=['POST'])
def borrar_integrantes():
    data = request.json
    documentos = data.get('documentos', [])

    Usuario_Equipo.query.filter(Usuario_Equipo.documento.in_(documentos)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({"mensaje": "Integrantes eliminados exitosamente"}), 200

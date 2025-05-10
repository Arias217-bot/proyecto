# routes/videos_routes.py

import os
from flask import render_template, request, current_app, url_for, jsonify, abort
from werkzeug.utils import secure_filename

from models.usuario import Usuario
from models.deteccion import Deteccion
from models.modalidad import Modalidad

from routes.entidad_routes import EntidadRoutes
from models.videos import Videos
from config import db

# Extensiones permitidas para videos
ALLOWED_EXTENSIONS = {'mp4', 'webm', 'ogg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Creamos el Blueprint y las rutas genéricas
videos_routes = EntidadRoutes('videos', Videos)
videos_bp = videos_routes.bp
videos_bp.name = "videos"

@videos_bp.route('/upload', methods=['POST'], endpoint='upload')
def upload_video():
    nombre = request.form.get('nombre')
    file = request.files.get('video_file')
    documento = request.form.get('documento')  # o desde session / current_user
    id_modalidad = request.form.get('id_modalidad')
    id_deteccion = request.form.get('id_deteccion')

    # Validaciones
    if not nombre or not file or not allowed_file(file.filename):
        return jsonify({'error': 'Datos inválidos o formato no permitido'}), 400
    
    # Verificar que la modalidad y detección existen en la base de datos
    modalidad = Modalidad.query.get(id_modalidad)
    deteccion = Deteccion.query.get(id_deteccion)
    
    if not modalidad or not deteccion:
        return jsonify({'error': 'Modalidad o detección no válidas'}), 400

    # Asegura que exista la carpeta
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Guarda el archivo
    filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, filename))

    # Construye la URL pública
    video_url = url_for('static', filename=f'uploads/{filename}')

    # Crea el registro en la BD
    nuevo_video = Videos(
        nombre=nombre, 
        url=video_url, 
        documento_usuario=documento,
        id_modalidad=id_modalidad, 
        id_deteccion=id_deteccion
    )
    db.session.add(nuevo_video)
    db.session.commit()

    return jsonify(nuevo_video.to_dict()), 201

# Ruta de lista / renderizado
@videos_bp.route('/ver', endpoint='videos_page')
def videos_page():
    query = request.args.get('q', '')
    if query:
        videos_list = Videos.query.filter(
            Videos.nombre.ilike(f"%{query}%")
        ).all()
    else:
        videos_list = Videos.query.all()

    return render_template(
        'videos.html',
        videos=videos_list,
        q=query
    )

@videos_bp.route('/ver/<documento>')
def videos_usuario(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    videos = (
        db.session.query(Videos)
          .join(Usuario, Videos.documento_usuario == Usuario.documento)
          .filter(Usuario.documento == documento)
          .all()
    )

    modalidades = (Modalidad.query.all())
    detecciones = (Deteccion.query.all())

    return render_template(
        'mis_videos.html',
        usuario=usuario,
        videos=[v.to_dict() for v in videos],
        modalidades=modalidades,
        detecciones=detecciones,
        documento=documento
    )

@videos_bp.route('/ver/<documento>/<nombre>', methods=['GET'])
def detalle_video(documento, nombre):
    # Buscar el video por documento del usuario y nombre normalizado
    nombre_normalizado = nombre.replace('-', ' ').lower()
    video = Videos.query.filter(
        Videos.documento_usuario == documento,
        db.func.lower(Videos.nombre) == nombre_normalizado
    ).first()

    if not video:
        abort(404, description="Video no encontrado")

    return render_template(
        'detalle_video.html',
        video=video
    )

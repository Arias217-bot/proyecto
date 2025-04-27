# routes/videos_routes.py

import os
from flask import render_template, request, current_app, url_for, jsonify
from werkzeug.utils import secure_filename

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

# Nuevo endpoint para subir archivos (multipart/form-data)
@videos_bp.route('/upload', methods=['POST'], endpoint='upload')
def upload_video():
    nombre = request.form.get('nombre')
    file = request.files.get('video_file')
    documento = request.form.get('documento_usuario')  # o desde session / current_user

    if not nombre or not file or not allowed_file(file.filename):
        return jsonify({'error': 'Datos inválidos o formato no permitido'}), 400

    # Asegura que exista la carpeta
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Guarda el archivo
    filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, filename))

    # Construye la URL pública
    video_url = url_for('static', filename=f'uploads/{filename}')

    # Crea el registro en la BD
    nuevo = Videos(nombre=nombre, url=video_url, documento_usuario=documento)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify(nuevo.to_dict()), 201

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


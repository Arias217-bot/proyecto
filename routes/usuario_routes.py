from flask import request, jsonify, render_template
from config import db
from models.usuario import Usuario
# routes/usuario_routes.py
from routes.entidad_routes import EntidadRoutes  # Asegúrate de que esta línea esté presente
from models.usuario import Usuario
from flask import render_template
from config import db



# Blueprints
usuario_routes = EntidadRoutes('usuario', Usuario)
usuario_bp = usuario_routes.bp  # El Blueprint que usaremos en `app.py`

@usuario_bp.route('/ver/<documento>', methods=['GET', 'PATCH'])
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if request.method == 'GET':
        return render_template('profile.html', usuario=usuario, documento=documento)

    if request.method == 'PATCH':
        data = request.get_json()
        
        # Aquí se actualizan solo los campos que se envían en la solicitud
        if 'fecha_nacimiento' in data:
            usuario.fecha_nacimiento = data['fecha_nacimiento']
        if 'telefono' in data:
            usuario.telefono = data['telefono']
        if 'direccion' in data:
            usuario.direccion = data['direccion']
        if 'experiencia' in data:
            usuario.experiencia = data['experiencia']
        if 'peso' in data:
            usuario.peso = data['peso']
        if 'altura' in data:
            usuario.altura = data['altura']

        try:
            db.session.commit()
            return jsonify({'mensaje': 'Perfil actualizado correctamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Hubo un problema al actualizar el perfil'}), 500

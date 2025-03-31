# routes/routes.py
from flask import Blueprint, jsonify, request, render_template
from werkzeug.security import generate_password_hash
from models.usuario import Usuario
from config import db
from flask_jwt_extended import jwt_required, get_jwt_identity

from routes.entidad_routes import EntidadRoutes

# Modelos
from models.usuario import Usuario

# Blueprints
usuario_routes = EntidadRoutes('usuario', Usuario)
usuario_bp = usuario_routes.bp  # El Blueprint que usaremos en `app.py`

# Obtener el perfil del usuario
@usuario_bp.route('/profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_document = get_jwt_identity()
    usuario = Usuario.query.get(current_user_document)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return render_template('profile.html', usuario=usuario.to_dict())

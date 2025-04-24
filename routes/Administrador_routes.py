# routes/administrador_routes.py
from flask import Blueprint, render_template
from config import db
from models.usuario import Usuario

# Definir el Blueprint
administrador_bp = Blueprint('administrador_bp', __name__)

@administrador_bp.route('/ver/<documento>')  # Asegúrate de que la URL tenga la variable <documento>
def administrador_page(documento):
    # Aquí puedes hacer una consulta a la base de datos con el documento
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('administrador.html', usuario=usuario, documento=documento)

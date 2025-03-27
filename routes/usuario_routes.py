# routes/usuario_routes.py
from flask import Blueprint, jsonify, request, render_template
from werkzeug.security import generate_password_hash
from models.usuario import Usuario
from config import db
from flask_jwt_extended import jwt_required, get_jwt_identity

usuario_bp = Blueprint('usuario_bp', __name__)

# Obtener todos los usuarios
@usuario_bp.route('/', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios])

# Agregar un nuevo usuario
@usuario_bp.route('/', methods=['POST'])
def add_usuario():
    data = request.json

    required_fields = ['documento', 'nombre', 'password', 'sexo', 'email', 'fecha_nacimiento']
    if not all(data.get(field) for field in required_fields):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Verificar si el correo ya está registrado
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    nuevo_usuario = Usuario(
        documento=data.get('documento'),
        nombre=data.get('nombre'),
        password=generate_password_hash(data.get('password')),
        fecha_nacimiento=data.get('fecha_nacimiento'),
        sexo=data.get('sexo'),
        telefono=data.get('telefono'),
        direccion=data.get('direccion'),
        email=data.get('email'),
        experiencia=data.get('experiencia')
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify(nuevo_usuario.to_dict()), 201

# Obtener un usuario por documento
@usuario_bp.route('/<string:documento>', methods=['GET'])
def get_usuario(documento):
    usuario = Usuario.query.get(documento)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuario.to_dict())

# Actualizar un usuario
@usuario_bp.route('/<string:documento>', methods=['PUT'])
def update_usuario(documento):
    usuario = Usuario.query.get(documento)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.json

    # Actualizar los campos si se proporcionan
    usuario.nombre = data.get('nombre', usuario.nombre)
    usuario.fecha_nacimiento = data.get('fecha_nacimiento', usuario.fecha_nacimiento)
    usuario.sexo = data.get('sexo', usuario.sexo)
    usuario.telefono = data.get('telefono', usuario.telefono)
    usuario.direccion = data.get('direccion', usuario.direccion)
    usuario.email = data.get('email', usuario.email)
    usuario.experiencia = data.get('experiencia', usuario.experiencia)

    # Actualizar la contraseña si se proporciona
    if 'password' in data and data['password']:
        usuario.password = generate_password_hash(data['password'])

    db.session.commit()

    return jsonify(usuario.to_dict()), 200

# Eliminar un usuario
@usuario_bp.route('/<string:documento>', methods=['DELETE'])
def delete_usuario(documento):
    usuario = Usuario.query.get(documento)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario eliminado"})

# Obtener el perfil del usuario
@usuario_bp.route('/profile', methods=['GET'])
@jwt_required()
def user_profile():
    current_user_document = get_jwt_identity()
    usuario = Usuario.query.get(current_user_document)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return render_template('profile.html', usuario=usuario.to_dict())

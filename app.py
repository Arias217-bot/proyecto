from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, unset_jwt_cookies
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta

from models.usuario import Usuario
from models.equipo import Equipo
from models.categoria_edad import CategoriaEdad
from models.categoria_sexo import CategoriaSexo

from config import init_db, db
from routes import blueprints

app = Flask(__name__)

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)

# Inicialización de la base de datos
init_db(app)

# Registro de rutas
for bp in blueprints:
    if bp.name == "usuario_bp":
        app.register_blueprint(bp, url_prefix='/usuarios')
    elif bp.name == "equipo_bp":
        app.register_blueprint(bp, url_prefix='/equipos')

# Rutas
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Correo y contraseña son requeridos'}), 400

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.password, password):
            access_token = create_access_token(identity=usuario.documento)
            return jsonify({
                'access_token': access_token,
                'documento': usuario.documento
            }), 200
        else:
            return jsonify({'error': 'Credenciales inválidas'}), 401

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"mensaje": "Sesión cerrada"})
    unset_jwt_cookies(response)
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    if not nombre or not email or not password:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400

    # Hashear la contraseña antes de almacenarla
    hashed_password = generate_password_hash(password)

    nuevo_usuario = Usuario(nombre=nombre, email=email, password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Usuario registrado exitosamente'}), 201


@app.context_processor
def inject_documento():
    try:
        documento = get_jwt_identity()
        return {'documento': documento}
    except:
        return {'documento': None}

@app.route('/perfil/<documento>')
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('profile.html', usuario=usuario, documento=documento)

@app.route('/perfil/<documento>/equipos')
def perfil_equipos(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    equipos = Equipo.query.all()  # O filtra por usuario si corresponde
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

@app.route('/perfil/<documento>/equipos/<int:id_equipo>/<nombre_equipo>')
def detalle_equipo(documento, id_equipo, nombre_equipo):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404

    equipo = db.session.get(Equipo, id_equipo)
    if not equipo or equipo.nombre.replace(" ", "-").lower() != nombre_equipo:
        return "Equipo no encontrado", 404

    # Obtener los nombres de las categorías
    categoria_edad = db.session.get(CategoriaEdad, equipo.id_categoria_edad)
    categoria_sexo = db.session.get(CategoriaSexo, equipo.id_categoria_sexo)

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
        documento=documento
    )

# Manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
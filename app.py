from flask import Flask, render_template, jsonify, request, session
from config import init_db
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, unset_jwt_cookies
from werkzeug.security import check_password_hash
from routes.usuario_routes import usuario_bp, user_profile
from datetime import timedelta
from models.usuario import Usuario
from config import db

app = Flask(__name__)

init_db(app)

# Clave secreta para JWT
app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)

# Registrar rutas
app.register_blueprint(usuario_bp, url_prefix='/usuarios')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET','POST'])
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

# Ruta de cerrar sesión
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"mensaje": "Sesión cerrada"})
    unset_jwt_cookies(response)
    return response

# Ruta para el registro de usuario
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# Ruta del perfil del usuario (protegida con JWT)
@app.route('/perfil', methods=['GET'])
@jwt_required()
def perfil_page():
    try:
        identidad = get_jwt_identity()
        return user_profile(render_template('perfil.html'))  
    except Exception as e:
        return jsonify({'error': 'Error al acceder al perfil de usuario', 'detalle': str(e)}), 500

@app.route('/perfil/<documento>')
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)  
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('profile.html', usuario=usuario)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

init_db(app)

# Clave secreta para JWT
app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)

# Registrar rutas
app.register_blueprint(usuario_bp, url_prefix='/usuarios')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET','POST'])
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

# Ruta de cerrar sesión
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"mensaje": "Sesión cerrada"})
    unset_jwt_cookies(response)
    return response

# Ruta para el registro de usuario
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# Ruta del perfil del usuario (protegida con JWT)
@app.route('/perfil', methods=['GET'])
@jwt_required()
def perfil_page():
    try:
        print(request.headers,"1")
        identidad = get_jwt_identity()
        print(request.headers,"2")
        print(f"Usuario autenticado: {identidad}")  # Aparece en la consola
        return user_profile(render_template('perfil.html'))  # Llama a la función que renderiza el perfil
    except Exception as e:
        return jsonify({'error': 'Error al acceder al perfil de usuario', 'detalle': str(e)}), 500

@app.route('/perfil/<documento>')
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)  # Obtener usuario por documento
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('profile.html', usuario=usuario)

if __name__ == '__main__':
    app.run(debug=True)

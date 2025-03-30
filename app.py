from flask import Flask, render_template, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, unset_jwt_cookies
from werkzeug.security import check_password_hash
from datetime import timedelta
from models.usuario import Usuario
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
    app.register_blueprint(bp, url_prefix='/usuarios')
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

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/perfil/<documento>')
def profile_page(documento):
    usuario = db.session.get(Usuario, documento)
    if not usuario:
        return "Usuario no encontrado", 404
    return render_template('profile.html', usuario=usuario)

# Manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
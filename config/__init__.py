# config/__init__.py
from flask_sqlalchemy import SQLAlchemy 

"""
    Algunas unidades simplemente no leen bien flask_sqlalchemy, vale la pena intentar si funciona apesar de que
    no se resuelva, he logrado conectarme a la base de datos aun con ese error
"""

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/bd_volleyball_prueba'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print("✅ Base de datos conectada con éxito")

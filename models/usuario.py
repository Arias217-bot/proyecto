# models/usuario.py
from config import db
from models.entidad_base import EntidadBase

class Usuario(EntidadBase):
    __tablename__ = 'usuario'

    documento = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(255))
    peso = db.Column(db.Float)
    altura = db.Column(db.Float)
    brado = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    experiencia = db.Column(db.Text)

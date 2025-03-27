# models/usuario.py
from config import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    documento = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    sexo = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True)
    experiencia = db.Column(db.Text)

    def to_dict(self):
        return {
            "documento": self.documento,
            "nombre": self.nombre,
            "fecha_nacimiento": self.fecha_nacimiento,
            "sexo": self.sexo,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "email": self.email,
            "experiencia": self.experiencia
        }
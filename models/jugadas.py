# models/jugadas.py
from config import db
from models.entidad_base import EntidadBase

class Jugadas(EntidadBase):
    __tablename__ = 'jugadas'

    id_jugada = db.Column(db.Integer, primary_key=True)
    id_partido = db.Column(db.Integer, nullable=False)
    secuencia_jugada = db.Column(db.Text)
    tiempo_inicio = db.Column(db.Time)
    tiempo_fin = db.Column(db.Time)

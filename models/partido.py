# models/partido.py
from config import db
from models.entidad_base import EntidadBase

class Partido(EntidadBase):
    __tablename__ = 'partido'

    id_torneo = db.Column(db.Integer, nullable=False)  # FK al torneo
    equipo_rival = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    marcador_local = db.Column(db.Integer, nullable=True)
    marcador_rival = db.Column(db.Integer, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
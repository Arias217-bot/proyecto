# models/partido.py
from config import db
from models.entidad_base import EntidadBase

class Partido(EntidadBase):
    __tablename__ = 'partido'

    id_partido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_torneo = db.Column(db.Integer, nullable=False)  # FK al torneo
    equipo_rival = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    marcador_local = db.Column(db.Integer, nullable=True)
    marcador_rival = db.Column(db.Integer, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    observaciones = db.Column(db.Text, nullable=True)

    def from_dict(self, data):
        """Asigna valores desde un diccionario."""
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self):
        """Devuelve un diccionario con los datos del partido."""
        return {
            'id_partido': self.id_partido,
            'id_torneo': self.id_torneo,
            'equipo_rival': self.equipo_rival,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'lugar': self.lugar,
            'marcador_local': self.marcador_local,
            'marcador_rival': self.marcador_rival,
            'video_url': self.video_url,
            'observaciones': self.observaciones
        }

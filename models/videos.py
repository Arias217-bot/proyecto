# models/video.py
from config import db
from models.entidad_base import EntidadBase

class Videos(EntidadBase):
    __tablename__ = 'videos'

    id_video = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    documento_usuario = db.Column(db.String(20), db.ForeignKey('usuario.documento'), nullable=False)

    # Relación con la tabla Usuario (para acceder fácilmente al usuario dueño del video)
    usuario = db.relationship('Usuario', backref=db.backref('videos', lazy=True))
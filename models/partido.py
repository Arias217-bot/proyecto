from config import db
from models.entidad_base import EntidadBase # Para heredar de EntidadBase

class Partido(EntidadBase):
    __tablename__ = 'partido'

    id_partido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.date)
    lugar = db.Column(db.String(100), nullable=False)
    resultado_local = db.Column(db.Integer, nullable=False)
    resultado_rival = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.Text)


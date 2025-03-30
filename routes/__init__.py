from flask import Blueprint
from .routes import *
from .equipo_routes import equipo_bp

# Definir los blueprints aquí para importarlos fácilmente
blueprints = [usuario_bp, equipo_bp]
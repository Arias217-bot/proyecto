from flask import Blueprint
from .usuario_routes import *
from .equipo_routes import equipo_bp

# Definir los blueprints aquí para importarlos fácilmente
blueprints = [usuario_bp, equipo_bp]
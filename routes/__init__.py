# routes/__init__.py
from .usuario_routes import usuario_bp
from .equipo_routes import equipo_bp
from .categoria_edad_routes import categoria_edad_bp

# Definir los blueprints aquí para importarlos fácilmente
blueprints = [usuario_bp, equipo_bp, categoria_edad_bp]



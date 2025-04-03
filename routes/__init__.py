# routes/__init__.py
from .usuario_routes import usuario_bp
from .equipo_routes import equipo_bp
from .categoria_edad_routes import categoria_edad_bp
from .categoria_sexo_routes import categoria_sexo_bp
from .jugadas_routes import jugadas_bp

# Definir los blueprints aquí para importarlos fácilmente
blueprints = [usuario_bp, equipo_bp, categoria_edad_bp, categoria_sexo_bp, jugadas_bp]

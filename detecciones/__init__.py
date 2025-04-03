from .deteccion_saque import evaluar_saque
from .deteccion_colocador import detectar_colocador
from .deteccion_ataque import detectar_ataque
from .deteccion_recibo import detectar_recibo

__all__ = [
    "evaluar_saque",
    "detectar_colocador",
    "detectar_ataque",
    "detectar_recibo"
]
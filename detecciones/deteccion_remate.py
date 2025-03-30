from evaluaciones.evaluar_contacto import evaluar_contacto
import math

def detectar_remate(landmarks):
    """
    Detecta y evalúa la técnica de remate.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Evaluar el contacto con el balón
        contacto_valido = evaluar_contacto(landmarks)

        # Mensajes descriptivos
        mensajes = [
            f"Remate {'válido' if contacto_valido['valido'] else 'no válido'}",
            contacto_valido["mensaje"]
        ]

        # Datos relevantes
        datos = [contacto_valido["valido"]]

        return {"mensajes": mensajes, "datos": datos}

    except Exception as e:
        print(f"Error en detectar_remate: {e}")
        return {"mensajes": ["Error en la detección de remate"], "datos": []}

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None
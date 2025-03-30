import math
from mediapipe.python.solutions.pose import PoseLandmark


def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        # Validar que los puntos sean del tipo esperado
        for punto in [p1, p2, p3]:
            if not hasattr(punto, 'x') or not hasattr(punto, 'y') or not hasattr(punto, 'z'):
                raise ValueError(f"Se esperaba un objeto Landmark, pero se recibió: {type(punto)}")

        # Calcular el ángulo entre los tres puntos
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def detectar_recibo(landmarks):
    """
    Detecta un recibo basado en los landmarks proporcionados.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Validar que landmarks sea una lista
        if not isinstance(landmarks, list):
            raise ValueError("Se esperaba una lista de landmarks, pero se recibió otro tipo de dato.")

        # Acceder a landmarks individuales
        tronco = landmarks[PoseLandmark.LEFT_HIP.value]
        rodilla = landmarks[PoseLandmark.LEFT_KNEE.value]
        tobillo = landmarks[PoseLandmark.LEFT_ANKLE.value]

        # Calcular ángulo de la rodilla
        angulo_rodilla = calcular_angulo(tronco, rodilla, tobillo)
        if angulo_rodilla is None:
            raise ValueError("No se pudo calcular el ángulo de la rodilla.")

        # Evaluar si el recibo es válido
        recibo_valido = angulo_rodilla > 90

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo de la rodilla: {angulo_rodilla:.2f}°",
            f"Recibo {'válido' if recibo_valido else 'no válido'}"
        ]

        return {"mensajes": mensajes, "datos": [angulo_rodilla, recibo_valido]}

    except Exception as e:
        print(f"Error en detectar_recibo: {e}")
        return {"mensajes": ["❌ Error en la detección de recibo"], "datos": []}
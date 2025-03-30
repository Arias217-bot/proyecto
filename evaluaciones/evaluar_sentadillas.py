import math
from mediapipe.python.solutions.pose import PoseLandmark


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

def evaluar_sentadilla(landmarks):
    """
    Evalúa la técnica de sentadilla basada en los landmarks proporcionados.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar que landmarks sea una lista
        if not isinstance(landmarks, list):
            raise ValueError("Se esperaba una lista de landmarks, pero se recibió otro tipo de dato.")

        # Acceder a landmarks individuales
        cadera = landmarks[PoseLandmark.LEFT_HIP.value]
        rodilla = landmarks[PoseLandmark.LEFT_KNEE.value]
        tobillo = landmarks[PoseLandmark.LEFT_ANKLE.value]

        # Calcular ángulo de la rodilla
        angulo_rodilla = calcular_angulo(cadera, rodilla, tobillo)
        if angulo_rodilla is None:
            raise ValueError("No se pudo calcular el ángulo de la rodilla.")

        # Evaluar si la sentadilla es válida
        sentadilla_valida = angulo_rodilla > 90 and angulo_rodilla < 140

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo de la rodilla: {angulo_rodilla:.2f}°",
            f"Sentadilla {'válida' if sentadilla_valida else 'no válida'}"
        ]

        return {"mensajes": mensajes, "datos": [angulo_rodilla, sentadilla_valida]}

    except Exception as e:
        print(f"Error en evaluar_sentadilla: {e}")
        return {"mensajes": ["❌ Error en la evaluación de la sentadilla"], "datos": []}
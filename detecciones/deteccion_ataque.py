import math
import mediapipe as mp
mp_pose = mp.solutions.pose
from evaluaciones.evaluar_contacto import evaluar_contacto  # Importar la evaluación de contacto
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

def detectar_ataque(landmarks):
    """
    Detecta un ataque basado en los landmarks proporcionados.
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
        hombro = landmarks[PoseLandmark.LEFT_SHOULDER.value]
        codo = landmarks[PoseLandmark.LEFT_ELBOW.value]
        muñeca = landmarks[PoseLandmark.LEFT_WRIST.value]

        # Calcular ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")

        # Evaluar si el ataque es válido
        ataque_valido = angulo_codo > 90

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo: {angulo_codo:.2f}°",
            f"Ataque {'válido' if ataque_valido else 'no válido'}"
        ]

        return {"mensajes": mensajes, "datos": [angulo_codo, ataque_valido]}

    except Exception as e:
        print(f"Error en detectar_ataque: {e}")
        return {"mensajes": ["❌ Error en la detección de ataque"], "datos": []}
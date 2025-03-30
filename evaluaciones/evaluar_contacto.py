import mediapipe as mp
import math
from mediapipe.python.solutions.pose import PoseLandmark

mp_pose = mp.solutions.pose

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

def evaluar_contacto(landmarks):
    """
    Evalúa si el contacto con el balón es correcto.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultado de la evaluación con un mensaje descriptivo y un indicador de validez.
    """
    try:
        # Validar que landmarks sea una lista
        if not isinstance(landmarks, list):
            raise ValueError("Se esperaba una lista de landmarks, pero se recibió otro tipo de dato.")

        # Acceder a landmarks individuales
        muñeca = landmarks[PoseLandmark.LEFT_WRIST.value]
        codo = landmarks[PoseLandmark.LEFT_ELBOW.value]
        hombro = landmarks[PoseLandmark.LEFT_SHOULDER.value]

        # Evaluar la posición relativa de la muñeca
        contacto_valido = muñeca.y < codo.y and codo.y < hombro.y

        # Mensaje descriptivo
        mensaje = (
            "✅ Contacto válido con el balón"
            if contacto_valido
            else "❌ Contacto incorrecto con el balón"
        )

        return {"mensaje": mensaje, "valido": contacto_valido}

    except Exception as e:
        print(f"Error en evaluar_contacto: {e}")
        return {"mensaje": "❌ Error al evaluar el contacto", "valido": False}
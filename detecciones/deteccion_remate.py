import math
from evaluaciones.evaluar_contacto import evaluar_contacto
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

def detectar_remate(landmarks):
    """
    Detecta y evalúa la técnica de remate.
    Args:
        landmarks (dict): Diccionario de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Validar que los landmarks esenciales estén presentes
        required_landmarks = [
            PoseLandmark.RIGHT_SHOULDER.value,
            PoseLandmark.RIGHT_ELBOW.value,
            PoseLandmark.RIGHT_WRIST.value
        ]
        if not isinstance(landmarks, dict) or not all(idx in landmarks for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para detectar el remate.")

        # Acceder a landmarks individuales
        hombro = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca = landmarks[PoseLandmark.RIGHT_WRIST.value]

        mensajes = []

        # Evaluar el ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")
        if angulo_codo < 90:
            mensajes.append("❌ El codo no está correctamente flexionado antes del remate.")

        # Evaluar la altura del brazo
        if muñeca.y > hombro.y:
            mensajes.append("❌ La muñeca debe estar por encima del hombro antes del remate.")

        # Evaluar el contacto con el balón
        contacto_valido = evaluar_contacto(landmarks)
        mensajes.append(contacto_valido["mensaje"])

        # Resultado final
        remate_valido = contacto_valido["valido"] and angulo_codo >= 90 and muñeca.y < hombro.y
        mensajes.append(f"Remate {'válido' if remate_valido else 'no válido'}")

        return {"mensajes": mensajes, "datos": {"angulo_codo": angulo_codo, "remate_valido": remate_valido}}

    except Exception as e:
        print(f"Error en detectar_remate: {e}")
        return {"mensajes": ["❌ Error en la detección del remate"], "datos": {}}
import math
import mediapipe as mp

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

def detectar_bloqueo(landmarks):
    """
    Detecta y evalúa la técnica de bloqueo.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Calcular ángulos relevantes
        angulo_brazos = calcular_angulo(
            landmarks[11],  # Hombro izquierdo
            landmarks[13],  # Codo izquierdo
            landmarks[15]   # Muñeca izquierda
        )
        altura_bloqueo = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y

        # Evaluar si el bloqueo es válido
        bloqueo_valido = angulo_brazos > 160 and altura_bloqueo < 0.5

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo de brazos: {angulo_brazos:.2f}",
            f"Altura del bloqueo: {altura_bloqueo:.2f}",
            f"Bloqueo {'válido' if bloqueo_valido else 'no válido'}"
        ]

        # Datos relevantes
        datos = [angulo_brazos, altura_bloqueo, bloqueo_valido]

        return {"mensajes": mensajes, "datos": datos}

    except Exception as e:
        print(f"Error en detectar_bloqueo: {e}")
        return {"mensajes": ["Error en la detección de bloqueo"], "datos": []}
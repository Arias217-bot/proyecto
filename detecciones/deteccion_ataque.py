import math
import mediapipe as mp
from evaluaciones.evaluar_contacto import evaluar_contacto
from mediapipe.python.solutions.pose import PoseLandmark

mp_pose = mp.solutions.pose

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    if not all([p1, p2, p3]):  # Verificar que los puntos existen
        return None
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
        # Validar que los landmarks contienen los datos requeridos
        required_landmarks = [
            PoseLandmark.LEFT_SHOULDER.value, PoseLandmark.LEFT_ELBOW.value, PoseLandmark.LEFT_WRIST.value,
            PoseLandmark.RIGHT_SHOULDER.value, PoseLandmark.RIGHT_ELBOW.value, PoseLandmark.RIGHT_WRIST.value
        ]

        if not all(idx in landmarks for idx in required_landmarks):
            raise ValueError("Faltan landmarks en la detección.")

        # Acceder a landmarks individuales para ambos brazos
        hombro_izq, codo_izq, muñeca_izq = (
            landmarks[PoseLandmark.LEFT_SHOULDER.value],
            landmarks[PoseLandmark.LEFT_ELBOW.value],
            landmarks[PoseLandmark.LEFT_WRIST.value],
        )
        hombro_der, codo_der, muñeca_der = (
            landmarks[PoseLandmark.RIGHT_SHOULDER.value],
            landmarks[PoseLandmark.RIGHT_ELBOW.value],
            landmarks[PoseLandmark.RIGHT_WRIST.value],
        )

        # Calcular ángulos de los codos
        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_codo_der = calcular_angulo(hombro_der, codo_der, muñeca_der)

        if angulo_codo_izq is None or angulo_codo_der is None:
            raise ValueError("No se pudo calcular uno o más ángulos del codo.")

        # Evaluar si el ataque es válido (se considera válido si cualquiera de los brazos tiene el ángulo correcto)
        ataque_valido_izq = angulo_codo_izq > 90
        ataque_valido_der = angulo_codo_der > 90
        ataque_valido = ataque_valido_izq or ataque_valido_der

        # Evaluación de contacto con el balón
        contacto = evaluar_contacto(landmarks)

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo izquierdo: {angulo_codo_izq:.2f}° ({'válido' if ataque_valido_izq else 'no válido'})",
            f"Ángulo del codo derecho: {angulo_codo_der:.2f}° ({'válido' if ataque_valido_der else 'no válido'})",
            f"Ataque {'válido' if ataque_valido else 'no válido'}",
            f"Evaluación de contacto: {'correcto' if contacto else 'incorrecto'}"
        ]

        return {"mensajes": mensajes, "datos": [angulo_codo_izq, angulo_codo_der, ataque_valido, contacto]}

    except Exception as e:
        print(f"Error en detectar_ataque: {e}")
        return {"mensajes": ["Error en la detección de ataque"], "datos": []}
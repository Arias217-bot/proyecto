import cv2
import mediapipe as mp
import numpy as np
import math

from evaluaciones.evaluar_estabilidad import evaluar_estabilidad
from evaluaciones.evaluar_posicion import evaluar_posicion
from evaluaciones.evaluar_movimiento import evaluar_movimiento
from evaluaciones.evaluar_contacto import evaluar_contacto
from evaluaciones.evaluar_seguimiento import evaluar_seguimiento
from mediapipe.python.solutions.pose import PoseLandmark


# Inicializar Mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

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

def evaluar_saque(landmarks):
    """
    Evalúa un saque basado en los landmarks proporcionados.
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
        hombro = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca = landmarks[PoseLandmark.RIGHT_WRIST.value]

        # Calcular ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")

        # Evaluar si el saque es válido
        saque_valido = angulo_codo > 90

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo: {angulo_codo:.2f}°",
            f"Saque {'válido' if saque_valido else 'no válido'}"
        ]

        return {"mensajes": mensajes, "datos": [angulo_codo, saque_valido]}

    except Exception as e:
        print(f"Error en evaluar_saque: {e}")
        return {"mensajes": ["❌ Error en la evaluación del saque"], "datos": []}
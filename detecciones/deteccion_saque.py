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

def detectar_saque(landmarks):
    """
    Detecta un saque basado en los landmarks proporcionados.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la evaluación con mensajes y datos relevantes.
    """
    try:
        # Validar que landmarks sea una lista y contenga los landmarks necesarios
        required_landmarks = [
            PoseLandmark.RIGHT_SHOULDER.value,
            PoseLandmark.RIGHT_ELBOW.value,
            PoseLandmark.RIGHT_WRIST.value
        ]
        if not isinstance(landmarks, list) or not all(idx < len(landmarks) for idx in required_landmarks):
            raise ValueError("Faltan landmarks esenciales para evaluar el saque.")

        # Acceder a landmarks individuales
        hombro = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca = landmarks[PoseLandmark.RIGHT_WRIST.value]

        # Validar altura inicial del brazo (muñeca debe estar por encima del hombro)
        altura_inicial_valida = muñeca.y < hombro.y
        if not altura_inicial_valida:
            return {
                "mensajes": ["❌ El brazo debe iniciar en una posición elevada."],
                "datos": []
            }

        # Calcular ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")

        # Evaluar alineación del brazo (hombro, codo y muñeca deben estar alineados)
        alineacion_hombro = abs(hombro.x - codo.x) < 0.1
        alineacion_codo = abs(codo.x - muñeca.x) < 0.1

        # Evaluar si el saque es válido
        saque_valido = angulo_codo > 90 and alineacion_hombro and alineacion_codo

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo del codo: {angulo_codo:.2f}°",
            f"Saque {'válido' if saque_valido else 'no válido'}"
        ]
        if not alineacion_hombro:
            mensajes.append("❌ Alinear mejor el hombro con el codo.")
        if not alineacion_codo:
            mensajes.append("❌ Alinear mejor el codo con la muñeca.")

        return {"mensajes": mensajes, "datos": [angulo_codo, saque_valido]}

    except Exception as e:
        print(f"Error en detectar_saque: {e}")
        return {"mensajes": ["❌ Error en la detección del saque"], "datos": []}
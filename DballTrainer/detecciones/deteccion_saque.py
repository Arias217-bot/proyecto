import cv2
import mediapipe as mp
import numpy as np

from evaluaciones.evaluar_estabilidad import evaluar_estabilidad
from evaluaciones.evaluar_posicion import evaluar_posicion
from evaluaciones.evaluar_movimiento import evaluar_movimiento
from evaluaciones.evaluar_contacto import evaluar_contacto
from evaluaciones.evaluar_seguimiento import evaluar_seguimiento

# Inicializar Mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

def calcular_angulo(a, b, c):
    """
    Calcula el ángulo entre tres puntos.
    
    Args:
        a, b, c: Coordenadas de los puntos.
    
    Returns:
        float: Ángulo en grados.
    """
    a = np.array(a)  # Primer punto
    b = np.array(b)  # Punto medio
    c = np.array(c)  # Último punto
    
    # Calcular los vectores entre los puntos
    ba = a - b
    bc = c - b

    # Calcular el ángulo entre los vectores
    coseno_angulo = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno_angulo)  # Ángulo en radianes
    return np.degrees(angulo)  # Convertir a grados

def evaluar_saque(landmarks):
    """
    Evalúa la postura del saque basado en los puntos de referencia del cuerpo.
    
    Args:
        landmarks: Lista de puntos de referencia del cuerpo.
    
    Returns:
        tuple: Ángulos y evaluación de la postura del saque.
    """
    # Extraer coordenadas necesarias
    hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
    codo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
    muñeca_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
    
    cadera_izq = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    rodilla_izq = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    tobillo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
    
    ojo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_EYE].x, landmarks[mp_pose.PoseLandmark.LEFT_EYE].y]
    ojo_der = [landmarks[mp_pose.PoseLandmark.RIGHT_EYE].x, landmarks[mp_pose.PoseLandmark.RIGHT_EYE].y]
    ojos = [(ojo_izq[0] + ojo_der[0]) / 2, (ojo_izq[1] + ojo_der[1]) / 2]  # Punto medio entre ambos ojos
    
    manos_sobre_frente = muñeca_izq[1] < ojos[1]  # Verificar si las manos están sobre la frente
    
    # Calcular los ángulos
    angulo_codo = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
    angulo_rodilla = calcular_angulo(cadera_izq, rodilla_izq, tobillo_izq)
    
    # Coordenadas adicionales para evaluar la estabilidad del tronco
    cadera_derecha = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
    hombro_derecho = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]

    # Calcular el ángulo del tronco (cadera-hombro-ojos)
    angulo_tronco = calcular_angulo(cadera_derecha, hombro_derecho, ojos)

    # Evaluación de la postura
    resultados = []
    if angulo_codo < 90:
        resultados.append('❌ Codo muy cerrado')
    elif angulo_codo > 120:
        resultados.append('❌ Codo muy abierto')
    else:
        resultados.append('✅ Codo correcto')

    if manos_sobre_frente:
        resultados.append('✅ Manos sobre la frente')
    else:
        resultados.append('❌ Subir manos sobre la frente')

    if 100 <= angulo_rodilla <= 140:
        resultados.append('✅ Rodilla correcta')
    else:
        resultados.append('❌ Ajustar rodilla')

    if 75 <= angulo_tronco <= 105:
        resultados.append('✅ Tronco estable')
    else:
        resultados.append('❌ Ajustar estabilidad del tronco')

    evaluacion = "\n".join(resultados)
    return angulo_codo, angulo_rodilla, angulo_tronco, manos_sobre_frente, evaluacion
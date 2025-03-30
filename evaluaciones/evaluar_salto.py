import time

import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_salto(landmarks, tiempo_inicio, tiempo_fin):
    """
    Evalúa la altura y el tiempo de vuelo del salto.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
        tiempo_inicio (float): Tiempo en el que el salto comenzó.
        tiempo_fin (float): Tiempo en el que el salto terminó.
    Returns:
        dict: Resultado de la evaluación con altura, tiempo de vuelo y mensaje descriptivo.
    """
    try:
        # Obtener la altura máxima del salto (posición Y del pie más bajo)
        altura_pie = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y
        tiempo_vuelo = tiempo_fin - tiempo_inicio

        # Mensaje descriptivo
        mensaje = f"Altura del salto: {altura_pie:.2f}, Tiempo de vuelo: {tiempo_vuelo:.2f}s"

        return {"mensaje": mensaje, "altura": altura_pie, "tiempo_vuelo": tiempo_vuelo}

    except Exception as e:
        print(f"Error en evaluar_salto: {e}")
        return {"mensaje": "❌ Error al evaluar el salto", "altura": 0, "tiempo_vuelo": 0}
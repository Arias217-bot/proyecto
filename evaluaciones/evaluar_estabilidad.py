import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_estabilidad(landmarks):
    """
    Evalúa la estabilidad del usuario basándose en la posición de los pies.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultado de la evaluación con un mensaje descriptivo y un indicador de estabilidad.
    """
    try:
        # Obtener los landmarks de los pies
        pie_derecho = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
        pie_izquierdo = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]

        # Calcular la diferencia en la posición vertical (eje Y) entre los pies
        diferencia_y = abs(pie_derecho.y - pie_izquierdo.y)

        # Condición para determinar la estabilidad
        estabilidad_correcta = diferencia_y < 0.1  # Umbral ajustable

        # Mensaje descriptivo
        if estabilidad_correcta:
            mensaje = "✅ Estabilidad correcta"
        else:
            mensaje = f"❌ Ajustar estabilidad (diferencia Y: {diferencia_y:.2f})"

        return {"mensaje": mensaje, "estable": estabilidad_correcta}

    except Exception as e:
        print(f"Error en evaluar_estabilidad: {e}")
        return {"mensaje": "❌ Error al evaluar la estabilidad", "estable": False}
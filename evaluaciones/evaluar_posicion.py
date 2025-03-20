import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_posicion(landmarks):
    """
    Evalúa la posición inicial basada en los puntos de referencia del cuerpo.
    
    Args:
        landmarks: Lista de puntos de referencia del cuerpo.
    
    Returns:
        str: Resultado de la evaluación de la posición inicial.
    """
    try:
        hombro = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        pie_derecho = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].x, landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].y]
    except KeyError as e:
        return f"Error: Punto de referencia no encontrado - {e}"

    # Lógica para evaluar la posición inicial
    if hombro[1] < pie_derecho[1]:  # Ejemplo de condición
        return "✅ Posición inicial correcta"
    else:
        return "❌ Ajustar posición inicial"
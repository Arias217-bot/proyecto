import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_estabilidad(landmarks):
    pie_derecho = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
    pie_izquierdo = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]

    # Lógica para evaluar la estabilidad
    if abs(pie_derecho.y - pie_izquierdo.y) < 0.1:  # Ejemplo de condición
        return "✅ Estabilidad correcta"
    else:
        return "❌ Ajustar estabilidad"
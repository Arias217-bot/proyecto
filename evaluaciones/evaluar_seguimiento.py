import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_seguimiento(landmarks):
    codo = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
    hombro = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]

    # Lógica para evaluar el seguimiento
    if codo.y < hombro.y:  # Ejemplo de condición
        return "✅ Seguimiento correcto"
    else:
        return "❌ Ajustar seguimiento"
import mediapipe as mp

mp_pose = mp.solutions.pose


def evaluar_movimiento(landmarks):
    cadera = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    hombro = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]

    # Lógica para evaluar el movimiento de preparación
    if cadera.y < hombro.y:  # Ejemplo de condición
        return "✅ Movimiento de preparación correcto"
    else:
        return "❌ Ajustar movimiento de preparación"
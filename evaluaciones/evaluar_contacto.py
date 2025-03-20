import mediapipe as mp

mp_pose = mp.solutions.pose

def evaluar_contacto(landmarks):
    muñeca = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    codo = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]

    # Lógica para evaluar el contacto con el balón
    if muñeca.y < codo.y:  # Ejemplo de condición
        return "✅ Contacto correcto con el balón"
    else:
        return "❌ Ajustar contacto con el balón"
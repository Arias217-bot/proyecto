import cv2
import mediapipe as mp
import numpy as np
import time
from evaluaciones.evaluar_contacto import evaluar_contacto
from evaluaciones.evaluar_posicion import evaluar_posicion
from evaluaciones.evaluar_movimiento import evaluar_movimiento
from evaluaciones.evaluar_estabilidad import evaluar_estabilidad
from evaluaciones.evaluar_sentadillas import evaluar_sentadillas

# Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calcular_angulo(a, b, c):
    """Calcula el ángulo entre tres puntos en coordenadas de píxeles."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cos_angulo = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(np.clip(cos_angulo, -1.0, 1.0))
    return np.degrees(angulo)

# Configuración de captura de video
use_webcam = True
video_path = r'C:\pryDballTrainer\Videos\Setter2.mp4'
cap = cv2.VideoCapture(0 if use_webcam else video_path)

if not cap.isOpened():
    print("Error: No se pudo abrir la fuente de video.")
    exit()

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    prev_time = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Fin del video o error en la captura.")
            break

        height, width, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        frame_output = frame.copy()

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame_output, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = results.pose_landmarks.landmark

            # Obtener puntos clave para ambos lados
            puntos_clave = {
                "izquierdo": {
                    "hombro": (int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * width),
                               int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)),
                    "codo": (int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x * width),
                             int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y * height)),
                    "muñeca": (int(landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x * width),
                               int(landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y * height))
                },
                "derecho": {
                    "hombro": (int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width),
                               int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)),
                    "codo": (int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x * width),
                             int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y * height)),
                    "muñeca": (int(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x * width),
                               int(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y * height))
                }
            }

            # Evaluaciones para ambos lados
            evaluaciones = {}
            for lado, puntos in puntos_clave.items():
                angulo_codo = calcular_angulo(puntos["hombro"], puntos["codo"], puntos["muñeca"])
                posicion_correcta = evaluar_posicion(landmarks)
                contacto_brazos = evaluar_contacto([landmarks[mp_pose.PoseLandmark.LEFT_WRIST],
                                                    landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]])
                estabilidad = evaluar_estabilidad(landmarks)
                sentadilla_correcta = evaluar_sentadillas(landmarks)
                movimiento_excesivo = evaluar_movimiento(landmarks)

                evaluaciones[lado] = {
                    "angulo_codo": angulo_codo,
                    "posicion_correcta": posicion_correcta,
                    "contacto_brazos": contacto_brazos,
                    "estabilidad": estabilidad,
                    "sentadilla_correcta": sentadilla_correcta,
                    "movimiento_excesivo": movimiento_excesivo
                }

            # Mensajes de evaluación
            mensajes = []
            for lado, evals in evaluaciones.items():
                estado = f"{lado.capitalize()} - Postura Correcta" if 80 <= evals["angulo_codo"] <= 100 else f"{lado.capitalize()} - Postura Incorrecta"
                color = (0, 255, 0) if "Correcta" in estado else (0, 0, 255)

                mensajes.append(estado)
                mensajes.append(f"{lado.capitalize()} - Posición corporal correcta" if evals["posicion_correcta"] else f"{lado.capitalize()} - Ajustar posición")
                mensajes.append(f"{lado.capitalize()} - Contacto de balón correcto" if evals["contacto_brazos"] else f"{lado.capitalize()} - Ajustar contacto de brazos")
                mensajes.append(f"{lado.capitalize()} - Estabilidad correcta" if evals["estabilidad"] else f"{lado.capitalize()} - Ajustar estabilidad")
                mensajes.append(f"{lado.capitalize()} - Profundidad de sentadilla correcta" if evals["sentadilla_correcta"] else f"{lado.capitalize()} - Ajustar profundidad de sentadilla")
                mensajes.append(f"{lado.capitalize()} - Movimiento controlado" if not evals["movimiento_excesivo"] else f"{lado.capitalize()} - Reducir movimiento innecesario")

            # Mostrar en pantalla
            for i, msg in enumerate(mensajes):
                cv2.putText(frame_output, msg, (50, 50 + (i * 30)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Dibujar puntos clave
            for lado, puntos in puntos_clave.items():
                cv2.circle(frame_output, puntos["hombro"], 5, (255, 0, 0), -1)
                cv2.circle(frame_output, puntos["codo"], 5, (0, 255, 0), -1)
                cv2.circle(frame_output, puntos["muñeca"], 5, (0, 0, 255), -1)

        # Calcular FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time

        cv2.putText(frame_output, f"FPS: {int(fps)}", (width - 150, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow('Evaluación de Postura', frame_output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

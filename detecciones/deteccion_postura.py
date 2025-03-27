import cv2
import mediapipe as mp
import numpy as np

# Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Función para calcular ángulos entre tres puntos
def calcular_angulo(a, b, c):
    a = np.array(a)  # Punto 1
    b = np.array(b)  # Punto central
    c = np.array(c)  # Punto 2

    ba = a - b
    bc = c - b

    coseno_angulo = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno_angulo)  # En radianes
    return np.degrees(angulo)  # Convertir a grados

# Captura de video
#cap = cv2.VideoCapture(r'C:\pryDballTrainer\Videos\Setter2.mp4')  # Usa 0 para webcam
cap = cv2.VideoCapture(0)  # Usa 0 para webcam

# Usar "with" para manejar mejor la memoria de Mediapipe
with mp_pose.Pose() as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir la imagen a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        # Crear copia para dibujar
        frame_output = frame.copy()

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame_output, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Obtener puntos clave
            landmarks = results.pose_landmarks.landmark
            codo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
            hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
            muñeca_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]

            # Calcular ángulo del codo izquierdo
            angulo_codo = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)

            # Definir si la postura es correcta (ejemplo: un pase de dedos debe tener codos entre 80° y 100°)
            if 80 <= angulo_codo <= 100:
                estado = "Postura Correcta"
                color = (0, 255, 0)  # Verde
            else:
                estado = "Postura Incorrecta"
                color = (0, 0, 255)  # Rojo

            # Mostrar ángulo y estado en pantalla
            cv2.putText(frame_output, f"Angulo Codo: {int(angulo_codo)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame_output, estado, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Mostrar la imagen con la evaluación de postura
        cv2.imshow('Detección de Postura', frame_output)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

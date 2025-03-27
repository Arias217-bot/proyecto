import cv2
import mediapipe as mp

# Inicializar Mediapipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# Captura de video (0 para webcam, o usa "video.mp4" para un archivo)
cap = cv2.VideoCapture('HowToTimeAVolleyball.mp4')
#cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir la imagen a RGB (Mediapipe usa RGB en vez de BGR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    # Dibujar los puntos y conexiones del cuerpo si se detectan
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Mostrar la imagen con las marcas del cuerpo
    cv2.imshow('Detección de Postura', frame)

    # Presiona 'q' para salir
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

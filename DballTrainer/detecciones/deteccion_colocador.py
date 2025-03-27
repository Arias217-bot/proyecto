import cv2
import mediapipe as mp
import numpy as np
import csv

# Crear archivo CSV y escribir encabezados
with open('analisis_postura.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Frame', 'Angulo Codo', 'Angulo Rodilla', 'Angulo Tronco', 'Manos Sobre Frente'])

# Inicializar Mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

def calcular_angulo(a, b, c):
    """
    Calcula el ángulo entre tres puntos.
    
    Args:
        a, b, c: Coordenadas de los puntos.
    
    Returns:
        float: Ángulo en grados.
    """
    a = np.array(a)  # Primer punto
    b = np.array(b)  # Punto medio
    c = np.array(c)  # Último punto
    
    # Calcular los vectores entre los puntos
    ba = a - b
    bc = c - b

    # Calcular el ángulo entre los vectores
    coseno_angulo = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angulo = np.arccos(coseno_angulo)  # Ángulo en radianes
    return np.degrees(angulo)  # Convertir a grados

def detectar_colocador(landmarks):
    """
    Detecta la postura del colocador basado en los puntos de referencia del cuerpo.
    
    Args:
        landmarks: Lista de puntos de referencia del cuerpo.
    
    Returns:
        tuple: Ángulos y evaluación de la postura del colocador.
    """
    # Extraer coordenadas necesarias
    hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y]
    codo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y]
    muñeca_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
    
    cadera_izq = [landmarks[mp_pose.PoseLandmark.LEFT_HIP].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP].y]
    rodilla_izq = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
    tobillo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
    
    ojo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_EYE].x, landmarks[mp_pose.PoseLandmark.LEFT_EYE].y]
    ojo_der = [landmarks[mp_pose.PoseLandmark.RIGHT_EYE].x, landmarks[mp_pose.PoseLandmark.RIGHT_EYE].y]
    ojos = [(ojo_izq[0] + ojo_der[0]) / 2, (ojo_izq[1] + ojo_der[1]) / 2]  # Punto medio entre ambos ojos
    
    manos_sobre_frente = muñeca_izq[1] < ojos[1]  # Verificar si las manos están sobre la frente
    
    # Calcular los ángulos
    angulo_codo = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
    angulo_rodilla = calcular_angulo(cadera_izq, rodilla_izq, tobillo_izq)
    
    # Coordenadas adicionales para evaluar la estabilidad del tronco
    cadera_derecha = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y]
    hombro_derecho = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y]

    # Calcular el ángulo del tronco (cadera-hombro-ojos)
    angulo_tronco = calcular_angulo(cadera_derecha, hombro_derecho, ojos)

    # Evaluación de la postura
    resultados = []
    if angulo_codo < 90:
        resultados.append('❌ Codo muy cerrado')
    elif angulo_codo > 120:
        resultados.append('❌ Codo muy abierto')
    else:
        resultados.append('✅ Codo correcto')

    if manos_sobre_frente:
        resultados.append('✅ Manos sobre la frente')
    else:
        resultados.append('❌ Subir manos sobre la frente')

    if 100 <= angulo_rodilla <= 140:
        resultados.append('✅ Rodilla correcta')
    else:
        resultados.append('❌ Ajustar rodilla')

    if 75 <= angulo_tronco <= 105:
        resultados.append('✅ Tronco estable')
    else:
        resultados.append('❌ Ajustar estabilidad del tronco')

    evaluacion = "\n".join(resultados)
    return angulo_codo, angulo_rodilla, angulo_tronco, manos_sobre_frente, evaluacion

# Cargar el video
cap = cv2.VideoCapture('HowToTimeAVolleyball.mp4')  # Cambia esto por la ruta del video

# Inicializar grabación de video
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir la imagen a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        # Dibujar los puntos clave del cuerpo
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        # Obtener los puntos clave
        landmarks = results.pose_landmarks.landmark
        
        # Detectar colocador y obtener resultados
        angulo_codo, angulo_rodilla, angulo_tronco, manos_sobre_frente, evaluacion = detectar_colocador(landmarks)

        # Guardar datos en el archivo CSV
        with open('analisis_postura.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([cap.get(cv2.CAP_PROP_POS_FRAMES),  # Número de cuadro
                             angulo_codo, 
                             angulo_rodilla, 
                             angulo_tronco, 
                             manos_sobre_frente])

        # Dibujar los resultados en la pantalla
        y0, dy = 50, 30
        for i, line in enumerate(evaluacion.split('\n')):
            y = y0 + i * dy
            cv2.putText(frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if '✅' in line else (0, 0, 255), 2)
    
    # Mostrar el video con la detección y los ángulos
    cv2.imshow('Evaluación de Postura - Colocador', frame)
    
    # Grabar el video
    out.write(frame)
    
    # Salir con la tecla 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
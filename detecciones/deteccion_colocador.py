import cv2
import mediapipe as mp
import numpy as np
import csv
import math
from mediapipe.python.solutions.pose import PoseLandmark


# Inicializar el archivo CSV
csv_file = open('analisis_postura.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Frame', 'Angulo Codo Izq', 'Angulo Rodilla Izq', 'Angulo Tronco Izq', 'Mano Izq Sobre Frente',
                     'Angulo Codo Der', 'Angulo Rodilla Der', 'Angulo Tronco Der', 'Mano Der Sobre Frente'])

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
        float: Ángulo en grados o None si no se puede calcular.
    """
    try:
        a = [a.x, a.y]  # Primer punto
        b = [b.x, b.y]  # Punto medio
        c = [c.x, c.y]  # Último punto

        # Calcular los vectores entre los puntos
        ba = [a[0] - b[0], a[1] - b[1]]
        bc = [c[0] - b[0], c[1] - b[1]]

        # Verificar que los vectores no sean nulos
        if math.sqrt(ba[0]**2 + ba[1]**2) == 0 or math.sqrt(bc[0]**2 + bc[1]**2) == 0:
            return None  # Retorna None si no se puede calcular el ángulo

        # Calcular el ángulo entre los vectores
        coseno_angulo = (ba[0] * bc[0] + ba[1] * bc[1]) / (math.sqrt(ba[0]**2 + ba[1]**2) * math.sqrt(bc[0]**2 + bc[1]**2))
        angulo = math.acos(coseno_angulo)  # Ángulo en radianes
        return math.degrees(angulo)  # Convertir a grados
    except AttributeError:
        print("❌ Error: Uno de los landmarks no tiene las propiedades necesarias.")
        return None

def verificar_landmark(landmark):
    """
    Verifica si un landmark es confiable basado en su visibilidad.
    Args:
        landmark: Landmark de Mediapipe.
    Returns:
        bool: True si el landmark es confiable, False en caso contrario.
    """
    return hasattr(landmark, 'visibility') and landmark.visibility >= 0.5

def detectar_colocador(landmarks):
    """
    Detecta la postura del colocador basado en los puntos de referencia del cuerpo.
    Args:
        landmarks: Lista de puntos de referencia del cuerpo.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Acceder a landmarks individuales (lado izquierdo)
        hombro_izq = landmarks[PoseLandmark.LEFT_SHOULDER.value]
        codo_izq = landmarks[PoseLandmark.LEFT_ELBOW.value]
        muñeca_izq = landmarks[PoseLandmark.LEFT_WRIST.value]
        cadera_izq = landmarks[PoseLandmark.LEFT_HIP.value]
        rodilla_izq = landmarks[PoseLandmark.LEFT_KNEE.value]
        tobillo_izq = landmarks[PoseLandmark.LEFT_ANKLE.value]
        ceja_izq = landmarks[PoseLandmark.LEFT_EYE.value]

        # Acceder a landmarks individuales (lado derecho)
        hombro_der = landmarks[PoseLandmark.RIGHT_SHOULDER.value]
        codo_der = landmarks[PoseLandmark.RIGHT_ELBOW.value]
        muñeca_der = landmarks[PoseLandmark.RIGHT_WRIST.value]
        cadera_der = landmarks[PoseLandmark.RIGHT_HIP.value]
        rodilla_der = landmarks[PoseLandmark.RIGHT_KNEE.value]
        tobillo_der = landmarks[PoseLandmark.RIGHT_ANKLE.value]
        ceja_der = landmarks[PoseLandmark.RIGHT_EYE.value]

        # Calcular ángulos (lado izquierdo)
        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_rodilla_izq = calcular_angulo(cadera_izq, rodilla_izq, tobillo_izq)
        angulo_tronco_izq = calcular_angulo(hombro_izq, cadera_izq, rodilla_izq)

        # Calcular ángulos (lado derecho)
        angulo_codo_der = calcular_angulo(hombro_der, codo_der, muñeca_der)
        angulo_rodilla_der = calcular_angulo(cadera_der, rodilla_der, tobillo_der)
        angulo_tronco_der = calcular_angulo(hombro_der, cadera_der, rodilla_der)

        # Verificar si los ángulos son válidos
        if None in [angulo_codo_izq, angulo_rodilla_izq, angulo_tronco_izq,
                    angulo_codo_der, angulo_rodilla_der, angulo_tronco_der]:
            return {"mensajes": ["❌ No se pudieron calcular algunos ángulos"], "datos": []}

        # Evaluar si las manos están sobre la frente
        manos_sobre_frente_izq = muñeca_izq.y < ceja_izq.y
        manos_sobre_frente_der = muñeca_der.y < ceja_der.y

        # Evaluación de la postura
        resultados = []

        # Evaluar codo izquierdo
        if angulo_codo_izq < 90:
            resultados.append('❌ Codo izquierdo muy cerrado')
        elif angulo_codo_izq > 120:
            resultados.append('❌ Codo izquierdo muy abierto')
        else:
            resultados.append('✅ Codo izquierdo correcto')

        # Evaluar codo derecho
        if angulo_codo_der < 90:
            resultados.append('❌ Codo derecho muy cerrado')
        elif angulo_codo_der > 120:
            resultados.append('❌ Codo derecho muy abierto')
        else:
            resultados.append('✅ Codo derecho correcto')

        # Evaluar rodilla izquierda
        if 100 <= angulo_rodilla_izq <= 140:
            resultados.append('✅ Rodilla izquierda correcta')
        else:
            resultados.append('❌ Ajustar rodilla izquierda')

        # Evaluar rodilla derecha
        if 100 <= angulo_rodilla_der <= 140:
            resultados.append('✅ Rodilla derecha correcta')
        else:
            resultados.append('❌ Ajustar rodilla derecha')

        # Evaluar estabilidad del tronco (promedio de ambos lados)
        angulo_tronco_promedio = (angulo_tronco_izq + angulo_tronco_der) / 2
        if 80 <= angulo_tronco_promedio <= 100:
            resultados.append('✅ Tronco estable')
        else:
            resultados.append('❌ Ajustar estabilidad del tronco')

        # Evaluar manos sobre la frente
        if manos_sobre_frente_izq:
            resultados.append('✅ Mano izquierda sobre la frente')
        else:
            resultados.append('❌ Mano izquierda no está sobre la frente')

        if manos_sobre_frente_der:
            resultados.append('✅ Mano derecha sobre la frente')
        else:
            resultados.append('❌ Mano derecha no está sobre la frente')

        evaluacion = "\n".join(resultados)
        return {
            "mensajes": [evaluacion],
            "datos": [
                angulo_codo_izq, angulo_rodilla_izq, angulo_tronco_izq, manos_sobre_frente_izq,
                angulo_codo_der, angulo_rodilla_der, angulo_tronco_der, manos_sobre_frente_der
            ]
        }

    except Exception as e:
        print(f"Error en detectar_colocador: {e}")
        return {"mensajes": ["❌ Error en la detección del colocador"], "datos": []}

# Cargar el video
cap = cv2.VideoCapture('HowToTimeAVolleyball.mp4')  # Cambia esto por la ruta del video

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
        resultado = detectar_colocador(results.pose_landmarks.landmark)
        if resultado["datos"]:
            angulo_codo_izq, angulo_rodilla_izq, angulo_tronco_izq, manos_sobre_frente_izq, \
            angulo_codo_der, angulo_rodilla_der, angulo_tronco_der, manos_sobre_frente_der = resultado["datos"]
            evaluacion = resultado["mensajes"][0]  # Obtener el mensaje de evaluación
            # Guardar datos en el archivo CSV
            with open('analisis_postura.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([cap.get(cv2.CAP_PROP_POS_FRAMES),  # Número de cuadro
                                 angulo_codo_izq, 
                                 angulo_rodilla_izq, 
                                 angulo_tronco_izq, 
                                 manos_sobre_frente_izq,
                                 angulo_codo_der, 
                                 angulo_rodilla_der, 
                                 angulo_tronco_der, 
                                 manos_sobre_frente_der])
        else:
            print("❌ No se pudieron guardar los datos debido a errores en la detección.")
            evaluacion = "❌ Error en la detección del colocador"  # Mensaje de error predeterminado

        # Dibujar los resultados en la pantalla
        y0, dy = 50, 30
        for i, line in enumerate(evaluacion.split('\n')):
            y = y0 + i * dy
            color = (0, 255, 0) if '✅' in line else (0, 255, 255) if '⚠️' in line else (0, 0, 255)
            cv2.putText(frame, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
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

# Al final del programa
csv_file.close()
import cv2
import mediapipe as mp
import pandas as pd
import os
import math
import logging
from datetime import datetime, timedelta
from PIL import ImageFont, Image, ImageDraw

# Importar las evaluaciones y detecciones
from detecciones.deteccion_saque import evaluar_saque
from detecciones.deteccion_colocador import detectar_colocador
from evaluaciones.evaluar_sentadillas import evaluar_sentadilla
from detecciones.deteccion_ataque import detectar_ataque
from detecciones.deteccion_recibo import detectar_recibo

# Configurar logging para errores
os.makedirs("Salidas", exist_ok=True)  # Crear la carpeta si no existe
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def cargar_fuente():
    """Carga una fuente personalizada o usa una alternativa legible."""
    try:
        return ImageFont.truetype("fonts/static/OpenSans_Condensed-Italic.ttf", 24)
    except IOError:
        return ImageFont.truetype("arial.ttf", 24)

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        # Validar que los puntos sean del tipo esperado
        for punto in [p1, p2, p3]:
            if not hasattr(punto, 'x') or not hasattr(punto, 'y') or not hasattr(punto, 'z'):
                raise ValueError(f"Se esperaba un objeto Landmark, pero se recibió: {type(punto)}")

        # Calcular el ángulo entre los tres puntos
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def procesar_frame(frame, pose, deteccion_func, frame_number):
    """Procesa un frame y evalúa la detección."""
    try:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        evaluacion_resultados = {"mensajes": ["No se detectaron puntos de referencia"], "datos": []}
        datos_csv = [frame_number, None, None, None, None]  # Inicializar con valores por defecto

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Convertir landmarks a una lista estándar
            landmarks = list(results.pose_landmarks.landmark)

            # Pasar landmarks a la función de detección
            evaluacion_resultados = deteccion_func(landmarks)

            # Extraer datos para el CSV
            if "datos" in evaluacion_resultados and len(evaluacion_resultados["datos"]) == 4:
                datos_csv = [frame_number] + evaluacion_resultados["datos"]

        else:
            # Mensajes detallados sobre posibles problemas
            print("⚠️ No se detectaron landmarks. Posibles causas:")
            print("- La imagen está demasiado oscura.")
            print("- Hay múltiples personas en el frame.")
            print("- El cuerpo no está completamente visible.")

    except Exception as e:
        logging.error(f"Error procesando frame: {e}")
        evaluacion_resultados = {"mensajes": ["Error en la evaluación"], "datos": []}

    return frame, results, evaluacion_resultados, datos_csv

def guardar_resultados_csv(datos, nombre, encabezados):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/"""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)  # Crear la carpeta si no existe
    filename = os.path.join(carpeta_salida, f"resultados_{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df = pd.DataFrame(datos, columns=encabezados)
    df.to_csv(filename, index=False)
    print(f"Resultados guardados en {filename}")

def detectar_ataque(landmarks):
    try:
        # Asegurarse de que landmarks sea una lista válida
        if not isinstance(landmarks, list):
            raise ValueError("Se esperaba una lista de landmarks, pero se recibió otro tipo de dato.")

        # Acceder a landmarks individuales
        hombro = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        codo = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        muñeca = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

        # Calcular el ángulo del codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)
        if angulo_codo is None:
            raise ValueError("No se pudo calcular el ángulo del codo.")

        return {"mensajes": [f"Ángulo del codo: {angulo_codo:.2f}°"], "datos": [angulo_codo]}
    except Exception as e:
        print(f"Error en detectar_ataque: {e}")
        return {"mensajes": ["❌ Error en la detección de ataque"], "datos": []}

def elegir_opcion():
    """Muestra el menú y asegura una selección válida."""
    opciones = {
        "saque": evaluar_saque,
        "colocador": detectar_colocador,
        "sentadilla": evaluar_sentadilla,
        "ataque": detectar_ataque,
        "recibo": detectar_recibo
    }
    
    while True:
        print("\n=== Opciones disponibles ===")
        for opcion in opciones:
            print(f"  ➡️ {opcion.capitalize()}")

        seleccion = input("Elige la detección o evaluación: ").strip().lower()
        if seleccion in opciones:
            return seleccion, opciones[seleccion]
        print("⚠️ Opción no válida. Inténtalo de nuevo.")

def main():
    """Función principal del programa."""
    seleccion, deteccion_func = elegir_opcion()

    # Elegir la fuente de video
    fuente = input("Elige la fuente de video (video/camara): ").strip().lower()
    if fuente == "video":
        ruta_video = input("Ingresa la ruta del video (por ejemplo, Videos/mi_video.mp4): ").strip()
        if not os.path.exists(ruta_video):
            print(f"⚠️ El archivo {ruta_video} no existe. Verifica la ruta.")
            return
        cap = cv2.VideoCapture(ruta_video)
    elif fuente == "camara":
        cap = cv2.VideoCapture(0)
    else:
        print("⚠️ Opción no válida. Elige 'video' o 'camara'.")
        return

    if not cap.isOpened():
        print("⚠️ No se pudo abrir la fuente de video. Verifica la conexión.")
        return

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    datos_resultados = []

    # Crear encabezados para el CSV
    encabezados_csv = ["Frame", "Angulo Codo", "Angulo Rodilla", "Angulo Tronco", "Manos Sobre Frente"]

    frame_number = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("⚠️ No se pudo capturar el frame. Saliendo...")
                break

            # Procesar el frame y obtener resultados
            frame, results, evaluacion_resultados, datos_csv = procesar_frame(frame, pose, deteccion_func, frame_number)

            # Agregar datos al CSV
            datos_resultados.append(datos_csv)

            # Mostrar mensajes de evaluación en la consola
            if evaluacion_resultados["mensajes"]:
                for mensaje in evaluacion_resultados["mensajes"]:
                    print(mensaje)

            # Mostrar el frame procesado en la ventana
            cv2.imshow("Detección de Postura", frame)

            # Salir si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Finalizando la detección...")
                break

            frame_number += 1

    except Exception as e:
        logging.error(f"Error en el flujo principal: {e}")
        print("❌ Ocurrió un error inesperado. Revisa el archivo de logs para más detalles.")

    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()

        # Guardar resultados en el CSV
        guardar_resultados_csv(datos_resultados, seleccion, encabezados_csv)
        print("✅ Resultados guardados y recursos liberados.")

if __name__ == "__main__":
    main()

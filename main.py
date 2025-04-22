# Importación de librerías necesarias
import cv2
import mediapipe as mp
import pandas as pd
import os
import math
import logging
from datetime import datetime
from tkinter import Tk, filedialog, Label, Button, StringVar
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from multi_person_detector import MultiPersonDetector
from PIL import Image, ImageTk
import time

# Importar funciones de detección específicas desde el módulo detecciones
from detecciones import (
    detectar_saque,
    detectar_colocador,
    detectar_ataque,
    detectar_recibo,
    detectar_bloqueo
)

# Importar función para detección multipersona
from multi_person_detector import run_multiperson_detection
from models.classify_pose import classify_pose

# Configuración de logs para almacenar errores en una carpeta llamada logs
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Inicializar soluciones de MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) -
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        logging.error(f"Error al calcular el ángulo: {e}")
        return None

def procesar_frame(frame, pose, deteccion_func, frame_number):
    """Procesa un frame y evalúa la detección."""
    try:
        # Convertir imagen a RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # Diccionario por defecto si no hay landmarks
        evaluacion_resultados = {"mensajes": ["No se detectaron puntos de referencia"], "datos": []}

        # Si se detectan landmarks se dibujan y se evalúan
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = list(results.pose_landmarks.landmark)
            evaluacion_resultados = deteccion_func(landmarks)

        return frame, evaluacion_resultados
    except Exception as e:
        logging.error(f"Error procesando frame: {e}")
        return frame, {"mensajes": ["Error en la evaluación"], "datos": []}

# Importar encabezados desde un archivo de configuración
from utils.config import CSV_HEADERS

def guardar_resultados_csv(datos, path_video, deteccion):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/"""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Obtener nombre base del video
    nombre_video = os.path.splitext(os.path.basename(path_video))[0]
    filename = os.path.join(carpeta_salida, f"{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        # Obtener los encabezados correspondientes a la detección
        encabezados = CSV_HEADERS.get(deteccion, ["Frame", "Mensajes"])

        # Validar si hay datos
        if not datos:
            print("No hay datos para guardar en el CSV.")
            return

        # Crear DataFrame y guardar CSV
        df = pd.DataFrame(datos, columns=encabezados)
        df.to_csv(filename, index=False)
        print(f"Resultados guardados en: {filename}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo CSV: {e}")
        print("No se pudieron guardar los resultados.")

def procesar_video(video_path, deteccion_func, deteccion, output_path):
    """Procesa un video archivo frame a frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        return

    try:
        # Configurar el video de salida
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps <= 0 or frame_width <= 0 or frame_height <= 0:
            print("El video tiene propiedades no válidas.")
            cap.release()
            return

        out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        print(f"Guardando video procesado en: {output_path}")

        pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        datos_resultados = []
        frame_number = 0
        lock = Lock()

        # Procesamiento en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            while cap.isOpened():
                try:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    futures.append(executor.submit(procesar_frame, frame, pose, deteccion_func, frame_number))
                    frame_number += 1
                except Exception as e:
                    logging.error(f"Error al leer un frame: {e}")
                    break

            # Recoger los resultados de los futures
            for future in futures:
                try:
                    frame, evaluacion_resultados = future.result()
                    out.write(frame)
                    with lock:
                        datos_resultados.append([frame_number, *evaluacion_resultados["datos"]])
                except Exception as e:
                    logging.error(f"Error al procesar un futuro: {e}")

        guardar_resultados_csv(datos_resultados, video_path, deteccion)
        print("Video procesado y guardado correctamente.")
    except Exception as e:
        logging.error(f"Error en el procesamiento del video: {e}")
    finally:
        cap.release()
        out.release()

def procesar_video_camara(deteccion_func, deteccion):
    """Procesa video en tiempo real desde la cámara."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    # Definir propiedades de video en vivo
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20  # Aproximado para cámara

    # Crear carpeta Salidas
    os.makedirs("Salidas", exist_ok=True)
    nombre_archivo = f"camara_{deteccion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    output_path = os.path.join("Salidas", nombre_archivo)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Llamar procesamiento de frames en vivo
    procesar_frames(cap, out, pose, deteccion_func, deteccion, output_path)

def procesar_frames(cap, out, pose, deteccion_func, deteccion, output_path):
    """Procesa frames desde una fuente de video y guarda resultados."""
    frame_number = 0
    datos_resultados = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame, evaluacion_resultados = procesar_frame(frame, pose, deteccion_func, frame_number)

            # Mostrar video en pantalla
            cv2.imshow("Detección en Tiempo Real", frame)

            # Guardar frame procesado
            out.write(frame)

            # Guardar datos de evaluación
            datos_resultados.append([frame_number, *evaluacion_resultados["datos"]])

            # Salir si se presiona 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_number += 1

        print(f"Video guardado en: {output_path}")
        guardar_resultados_csv(datos_resultados, output_path, deteccion)
    except Exception as e:
        logging.error(f"Error procesando frames: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
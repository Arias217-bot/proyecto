# main.py (se llama integration.py)

# Importación de librerías necesarias
import cv2
import mediapipe as mp
import pandas as pd  # Aunque puede que no lo uses directamente para la API, se mantiene por la solicitud
import os
import math  # Ídem para math
import logging
from datetime import datetime
# from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu  # Comentado: interfaz gráfica
# from concurrent.futures import ThreadPoolExecutor  # Podría ser útil para tareas en segundo plano en la API
from pathlib import Path  # Útil para manejo de rutas
import json
from evaluaciones.evaluar_contacto import evaluar_contacto

# Importar funciones de detección específicas desde el módulo detecciones
from detecciones import (
    detectar_saque, obtener_encabezados_saque,
    detectar_colocador, obtener_encabezados_colocador,
    detectar_ataque, obtener_encabezados_ataque,
    detectar_recibo, obtener_encabezados_recibo,
    detectar_bloqueo, obtener_encabezados_bloqueo
)

# # Importar función para detección de múltiples personas (comentado ya que nos enfocamos en una persona)
# from multi_person_detector import MultiPersonDetector

# Configuración de logs para almacenar errores
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Inicializar soluciones de MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def analizar_video(video_path, deteccion):
    """
    Analiza un video para detectar una acción específica de voleibol en una sola persona.

    Args:
        video_path (str): Ruta al archivo de video.
        deteccion (str): Tipo de acción a detectar ('Saque', 'Colocador', etc.).

    Returns:
        list: Lista de diccionarios con los resultados del análisis.
              None si hay un error al abrir el video o la detección no es válida.
    """
    if deteccion not in funciones_deteccion:
        logging.error(f"Detección no válida: {deteccion}")
        print(f"Error: Detección no válida: {deteccion}")
        return None

    detectar_func, obtener_encabezados_func = funciones_deteccion[deteccion]

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"No se pudo abrir el video en: {video_path}")
        print(f"Error: No se pudo abrir el video en: {video_path}")
        return None

    resultados_json = []
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = list(results.pose_landmarks.landmark)
            evaluacion_resultados = detectar_func(landmarks)
            hay_contacto = evaluar_contacto(landmarks)

            resultados_frame = {
                "frame": frame_number,
                "timestamp": datetime.now().isoformat(),
                "deteccion": deteccion,
                "resultados_deteccion": evaluacion_resultados,
                "contacto": hay_contacto,
                "landmarks": [(lm.x, lm.y, lm.z, lm.visibility) for lm in landmarks]
            }
            resultados_json.append(resultados_frame)

        frame_number += 1

    cap.release()
    return resultados_json

def analizar_camara(deteccion):
    """
    Analiza la transmisión de la cámara en tiempo real para detectar una acción
    específica de voleibol en una sola persona.

    Args:
        deteccion (str): Tipo de acción a detectar.

    Returns:
        list: Lista de diccionarios con los resultados del análisis en tiempo real.
              El proceso se detiene al presionar 'q'.
              None si hay un error al abrir la cámara o la detección no es válida.
    """
    if deteccion not in funciones_deteccion:
        logging.error(f"Detección no válida: {deteccion}")
        print(f"Error: Detección no válida: {deteccion}")
        return None

    detectar_func, obtener_encabezados_func = funciones_deteccion[deteccion]

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("No se pudo abrir la cámara.")
        print("Error: No se pudo abrir la cámara.")
        return None

    resultados_json = []
    frame_number = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Opcional: voltear horizontalmente
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = list(results.pose_landmarks.landmark)
            evaluacion_resultados = detectar_func(landmarks)
            hay_contacto = evaluar_contacto(landmarks)

            resultados_frame = {
                "frame": frame_number,
                "timestamp": datetime.now().isoformat(),
                "deteccion": deteccion,
                "resultados_deteccion": evaluacion_resultados,
                "contacto": hay_contacto,
                "landmarks": [(lm.x, lm.y, lm.z, lm.visibility) for lm in landmarks]
            }
            resultados_json.append(resultados_frame)

            # Opcional: mostrar el frame con los landmarks para depuración local
            # mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            # cv2.imshow(f"Detección en vivo: {deteccion}", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows()
    return resultados_json

# Mapeo de la detección seleccionada a las funciones correspondientes
funciones_deteccion = {
    "Saque": (detectar_saque, obtener_encabezados_saque),
    "Colocador": (detectar_colocador, obtener_encabezados_colocador),
    "Ataque": (detectar_ataque, obtener_encabezados_ataque),
    "Recibo": (detectar_recibo, obtener_encabezados_recibo),
    "Bloqueo": (detectar_bloqueo, obtener_encabezados_bloqueo),
}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Script para análisis de voleibol (una persona) para API")
    parser.add_argument('--fuente', type=str, choices=['camara', 'video'], default='video', help='Fuente del video')
    parser.add_argument('--ruta_video', type=str, help='Ruta al archivo de video si la fuente es "video"')
    parser.add_argument('--deteccion', type=str, choices=list(funciones_deteccion.keys()), required=True, help='Acción a detectar')
    args = parser.parse_args()

    if args.fuente == 'video':
        if args.ruta_video:
            resultados = analizar_video(args.ruta_video, args.deteccion)
            if resultados:
                print(json.dumps(resultados, indent=4))
        else:
            print("Error: Debes especificar la ruta del video con --ruta_video.")
    elif args.fuente == 'camara':
        print(f"Iniciando análisis de la cámara para '{args.deteccion}'. Presiona Ctrl+C para detener.")
        resultados = analizar_camara(args.deteccion)
        if resultados:
            print(json.dumps(resultados, indent=4))
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
from models.classify_pose import ClassifyPose
from multi_person_detector import MultiPersonDetector

# Configuración de logs para almacenar errores en una carpeta llamada logs
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Inicializar soluciones de MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Función para seleccionar la modalidad
def seleccionar_modalidad():
    """Permite al usuario seleccionar entre los modos 'persona' o 'equipo'."""
    modalidad = None

    def seleccionar(m):
        nonlocal modalidad
        modalidad = m
        root.destroy()

    root = Tk()
    root.title("Seleccione Modalidad")
    label = Label(root, text="Seleccione una modalidad de análisis:")
    label.pack(pady=10)
    boton_persona = Button(root, text="Persona", command=lambda: seleccionar("persona"))
    boton_persona.pack(pady=5)
    boton_equipo = Button(root, text="Equipo", command=lambda: seleccionar("equipo"))
    boton_equipo.pack(pady=5)
    root.mainloop()
    return modalidad

# Función para seleccionar la detección
def seleccionar_deteccion():
    """Permite al usuario seleccionar una acción específica para analizar."""
    root = Tk()  # Inicializar la ventana raíz
    root.title("Seleccionar Detección")
    seleccion = StringVar(root)  # Asociar StringVar a la ventana raíz

    def seleccionar_opcion(opcion):
        seleccion.set(opcion)
        root.destroy()

    label = Label(root, text="Seleccione la detección que desea realizar:")
    label.pack(pady=10)

    opciones = {
        "Saque": "saque",
        "Colocador": "colocador",
        "Ataque": "ataque",
        "Recibo": "recibo",
        "Bloqueo": "bloqueo",
    }

    for texto, valor in opciones.items():
        boton = Button(root, text=texto, command=lambda v=valor: seleccionar_opcion(v))
        boton.pack(pady=5)

    root.mainloop()
    return seleccion.get()

# Función para seleccionar la fuente de video
def obtener_fuente_video():
    """Permite al usuario seleccionar entre usar la cámara o cargar un archivo de video."""
    root = Tk()  # Inicializar la ventana raíz
    root.title("Seleccionar Fuente de Video")
    seleccion = StringVar(root)  # Asociar StringVar a la ventana raíz

    def usar_video():
        seleccion.set("video")
        root.destroy()

    def usar_camara():
        seleccion.set("camara")
        root.destroy()

    label = Label(root, text="Seleccione la fuente de video:")
    label.pack(pady=10)

    boton_video = Button(root, text="Subir Video", command=usar_video)
    boton_video.pack(pady=5)

    boton_camara = Button(root, text="Usar Cámara", command=usar_camara)
    boton_camara.pack(pady=5)

    root.mainloop()

    if seleccion.get() == "video":
        video_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi")])
        if not video_path:
            print("No se seleccionó ningún archivo de video. Saliendo...")
            return None
        return video_path
    elif seleccion.get() == "camara":
        return 0  # Índice de la cámara
    else:
        print("No se seleccionó ninguna fuente de video. Saliendo...")
        return None

# Función para preguntar si se desea guardar el video procesado
def seleccionar_guardar_video():
    """Pregunta al usuario si desea guardar el video procesado."""
    root = Tk()  # Inicializar la ventana raíz
    root.title("Guardar Video Procesado")
    seleccion = StringVar(root)  # Asociar StringVar a la ventana raíz

    def seleccionar(opcion):
        seleccion.set(opcion)
        root.destroy()

    label = Label(root, text="¿Desea guardar el video procesado con overlay?")
    label.pack(pady=10)
    boton_si = Button(root, text="Sí", command=lambda: seleccionar("si"))
    boton_si.pack(pady=5)
    boton_no = Button(root, text="No", command=lambda: seleccionar("no"))
    boton_no.pack(pady=5)
    root.mainloop()

    return seleccion.get() == "si"

# Función para procesar un frame
def procesar_frame(frame, pose, deteccion_func):
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

def procesar_video(video_path, deteccion_func, deteccion, output_path):
    """Procesa un video y guarda el resultado en un archivo de video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    datos_resultados = []  # Lista para almacenar los resultados de evaluación
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, evaluacion_resultados = procesar_frame(frame, pose, deteccion_func)
        out.write(frame)

        # Guardar los resultados de evaluación
        datos_resultados.append([frame_number, *evaluacion_resultados["datos"]])
        frame_number += 1

        cv2.imshow(f"Procesando {deteccion}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video procesado guardado en: {output_path}")

    # Guardar los resultados en un archivo CSV
    guardar_resultados_csv(datos_resultados, video_path, deteccion)

def procesar_video_sin_guardar(video_path, deteccion_func, deteccion):
    """Procesa un video y muestra los resultados en pantalla sin guardar el archivo."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        return

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, _ = procesar_frame(frame, pose, deteccion_func)

        cv2.imshow(f"Procesando {deteccion}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def procesar_video_camara(deteccion_func, deteccion):
    """Procesa la cámara en tiempo real."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, _ = procesar_frame(frame, pose, deteccion_func)

        cv2.imshow(f"Procesando {deteccion}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def guardar_resultados_csv(datos, path_video, deteccion):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/."""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)  # Crear la carpeta si no existe

    # Extraer el nombre base del video
    nombre_video = os.path.splitext(os.path.basename(path_video))[0]
    filename = os.path.join(carpeta_salida, f"{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        # Definir encabezados específicos para cada detección
        encabezados = {
            "colocador": [
                "Frame", "Angulo Codo Izq", "Angulo Rodilla Izq", "Angulo Tronco Izq", "Mano Izq Sobre Frente",
                "Angulo Codo Der", "Angulo Rodilla Der", "Angulo Tronco Der", "Mano Der Sobre Frente",
                "Estabilidad", "Movimiento Controlado"
            ],
            "saque": [
                "Frame", "Angulo Codo", "Altura Brazo", "Velocidad Angular Codo", "Saque Valido",
                "Estabilidad", "Movimiento Controlado"
            ],
            "ataque": [
                "Frame", "Angulo Codo Izq", "Angulo Codo Der", "Velocidad Angular Codo Izq", "Velocidad Angular Codo Der",
                "Ataque Valido", "Contacto Valido", "Simetria", "Estabilidad", "Movimiento Controlado"
            ],
            "recibo": [
                "Frame", "Angulo Tronco", "Profundidad Sentadilla", "Posicion Correcta", "Contacto Brazos",
                "Estabilidad", "Movimiento Controlado", "Distancia Entre Pies"
            ],
            "bloqueo": [
                "Frame", "Angulo Brazo Izq", "Angulo Brazo Der", "Altura Bloqueo Izq", "Altura Bloqueo Der",
                "Alineacion Tronco", "Bloqueo Valido", "Separacion Manos", "Simetria", "Estabilidad"
            ]
        }.get(deteccion, ["Frame", "Mensajes"])

        # Validar que los datos coincidan con los encabezados
        if len(encabezados) != len(datos[0]):
            raise ValueError(f"Los datos no coinciden con los encabezados. Encabezados: {len(encabezados)}, Datos: {len(datos[0])}")

        # Crear el DataFrame con los datos y encabezados
        df = pd.DataFrame(datos, columns=encabezados)
        df.to_csv(filename, index=False)
        print(f"Resultados guardados en: {filename}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo CSV: {e}")
        print("No se pudieron guardar los resultados.")

# Función principal para iniciar el procesamiento
def iniciar_procesamiento():
    """Inicia el flujo principal del programa."""
    print("Iniciando procesamiento...")
    modalidad = seleccionar_modalidad()
    print(f"Modalidad seleccionada: {modalidad}")
    if not modalidad:
        print("No se seleccionó modalidad. Saliendo...")
        return

    if modalidad == "persona":
        deteccion = seleccionar_deteccion()
        print(f"Detección seleccionada: {deteccion}")
        if not deteccion:
            print("No se seleccionó ninguna detección. Saliendo...")
            return

        deteccion_func = {
            "saque": detectar_saque,
            "colocador": detectar_colocador,
            "ataque": detectar_ataque,
            "recibo": detectar_recibo,
            "bloqueo": detectar_bloqueo
        }.get(deteccion)

        if not deteccion_func:
            print("Detección no válida seleccionada. Saliendo...")
            return

        fuente = obtener_fuente_video()
        print(f"Fuente seleccionada: {fuente}")
        if fuente is None:
            print("No se seleccionó ninguna fuente de video. Saliendo...")
            return

        if isinstance(fuente, str):
            if seleccionar_guardar_video():
                nombre_video = os.path.splitext(os.path.basename(fuente))[0]
                output_path = os.path.join("Salidas", f"{deteccion}_{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                procesar_video(fuente, deteccion_func, deteccion, output_path)
            else:
                procesar_video_sin_guardar(fuente, deteccion_func, deteccion)
        else:
            procesar_video_camara(deteccion_func, deteccion)

    elif modalidad == "equipo":
        fuente = obtener_fuente_video()
        print(f"Fuente seleccionada: {fuente}")
        if fuente is None:
            print("No se seleccionó ninguna fuente de video. Saliendo...")
            return

        detector = MultiPersonDetector(model_url="https://tfhub.dev/google/movenet/multipose/lightning/1", output_dir="Salidas")
        if isinstance(fuente, str):
            detector.process_video_or_camera(fuente, os.path.join("Salidas", "equipo_output_video.avi"), os.path.join("Salidas", "equipo_output.csv"))
        else:
            detector.process_video_or_camera(0, os.path.join("Salidas", "equipo_output_video.avi"), os.path.join("Salidas", "equipo_output.csv"))

# Bloque principal
if __name__ == "__main__":
    iniciar_procesamiento()
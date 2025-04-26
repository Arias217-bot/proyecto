# Importación de librerías necesarias
import cv2
import mediapipe as mp
import pandas as pd
import os
import math
import logging
from datetime import datetime
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu
from concurrent.futures import ThreadPoolExecutor

# Importar funciones de detección específicas desde el módulo detecciones
from detecciones import (
    detectar_saque, obtener_encabezados_saque,
    detectar_colocador, obtener_encabezados_colocador,
    detectar_ataque, obtener_encabezados_ataque,
    detectar_recibo, obtener_encabezados_recibo,
    detectar_bloqueo, obtener_encabezados_bloqueo
)

# Importar función para detección multipersona
from models.classify_pose import ClassifyPose
from multi_person_detector import MultiPersonDetector
from utils.config import CSV_HEADERS  # Importar los encabezados centralizados

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
        "Saque": "Saque",
        "Colocador": "Colocador",
        "Ataque": "Ataque",
        "Recibo": "Recibo",
        "Bloqueo": "Bloqueo",
    }

    for texto, valor in opciones.items():
        boton = Button(root, text=texto, command=lambda v=valor: seleccionar_opcion(v))
        boton.pack(pady=5)

    root.mainloop()
    return seleccion.get()

# Función para seleccionar la fuente de video
def obtener_fuente_video():
    """Permite al usuario seleccionar entre usar la cámara o cargar un archivo de video."""
    try:
        root = Tk()
        root.title("Seleccionar Fuente de Video")
        seleccion = StringVar(root)

        def usar_video():
            seleccion.set("video")
            root.destroy()

        def usar_camara():
            seleccion.set("camara")
            root.destroy()

        Label(root, text="Seleccione la fuente de video:").pack(pady=10)
        Button(root, text="Subir Video", command=usar_video).pack(pady=5)
        Button(root, text="Usar Cámara", command=usar_camara).pack(pady=5)
        root.mainloop()

        if seleccion.get() == "video":
            video_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi")])
            if not video_path:
                raise ValueError("No se seleccionó ningún archivo de video.")
            return video_path
        elif seleccion.get() == "camara":
            return 0  # Índice de la cámara
        else:
            raise ValueError("No se seleccionó ninguna fuente de video.")
    except Exception as e:
        logging.error(f"Error al seleccionar fuente de video: {e}")
        print(f"Ocurrió un error: {e}. Consulte el log para más detalles.")
        return None

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
            print(f"Landmarks detectados en el frame: {landmarks}")
            evaluacion_resultados = deteccion_func(landmarks)  # Esta función debe devolver una lista de datos
            print(f"Datos generados por deteccion_func: {evaluacion_resultados}")

        return frame, evaluacion_resultados
    except Exception as e:
        raise RuntimeError(f"Error procesando frame: {e}")

def procesar_video(video_path, deteccion_func, deteccion, output_path):
    """Procesa un video y guarda el resultado en un archivo de video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir el video.")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 30
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))
    if not out.isOpened():
        raise RuntimeError("No se pudo crear el archivo de video de salida.")

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    datos_resultados = []  # Lista para almacenar los resultados de evaluación
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame. Fin del video o error.")
            break

        frame, evaluacion_resultados = procesar_frame(frame, pose, deteccion_func)

        # Limpiar los datos generados por deteccion_func
        datos_limpiados = []
        for valor in evaluacion_resultados["datos"]:
            if isinstance(valor, dict):  # Reemplazar diccionarios con un valor predeterminado
                datos_limpiados.append(False)  # O usar None si prefieres
            else:
                datos_limpiados.append(valor)

        # Agregar los datos al resultado final
        datos_resultados.append([frame_number, *datos_limpiados])
        frame_number += 1

        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video procesado guardado en: {output_path}")
    return datos_resultados

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

def guardar_resultados_csv(datos, path_video, deteccion, obtener_encabezados_func):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/"""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Extraer el nombre base del video y formatear la fecha
    nombre_video = os.path.splitext(os.path.basename(path_video))[0]
    fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(carpeta_salida, f"{nombre_video}_{deteccion}_{fecha}.csv")

    try:
        # Obtener encabezados dinámicos y agregar "Frame" al inicio
        encabezados = ["Frame"] + obtener_encabezados_func()

        # Crear el DataFrame con los datos y encabezados
        df = pd.DataFrame(datos, columns=encabezados)
        df.to_csv(filename, index=False)
        print(f"Resultados guardados en: {filename}")
    except Exception as e:
        logging.error(f"Error al guardar archivo CSV: {e}")
        print(f"Ocurrió un error al guardar los resultados: {e}")

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

        # Mapear detecciones a funciones de encabezados
        deteccion_func_map = {
            "Saque": (detectar_saque, obtener_encabezados_saque),
            "Colocador": (detectar_colocador, obtener_encabezados_colocador),
            "Ataque": (detectar_ataque, obtener_encabezados_ataque),
            "Recibo": (detectar_recibo, obtener_encabezados_recibo),
            "Bloqueo": (detectar_bloqueo, obtener_encabezados_bloqueo),
        }

        deteccion_func, obtener_encabezados_func = deteccion_func_map.get(deteccion, (None, None))
        if not deteccion_func or not obtener_encabezados_func:
            print("Detección no válida seleccionada. Saliendo...")
            return

        fuente = obtener_fuente_video()
        print(f"Fuente seleccionada: {fuente}")
        if fuente is None:
            print("No se seleccionó ninguna fuente de video. Saliendo...")
            return

        # Siempre guardar el video procesado
        print("El video será guardado.")
        if isinstance(fuente, str):  # Si la fuente es un archivo de video
            nombre_video = os.path.splitext(os.path.basename(fuente))[0]
            output_path = os.path.join("Salidas", f"{deteccion}_{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

            datos_resultados = procesar_video(fuente, deteccion_func, deteccion, output_path)
            guardar_resultados_csv(datos_resultados, fuente, deteccion, obtener_encabezados_func)
        else:  # Si la fuente es la cámara
            output_path = os.path.join("Salidas", f"{deteccion}_camara_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
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
def main():
    """Función principal para iniciar el programa."""
    print("Bienvenido a DballTrainer - Análisis Técnico de Voleibol")
    print("Iniciando el programa...")
    try:
        iniciar_procesamiento()
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        print("Ocurrió un error inesperado. Por favor, revise el archivo de logs para más detalles.")

if __name__ == "__main__":
    main()
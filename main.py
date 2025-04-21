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

# Importar las detecciones desde el paquete modular
from detecciones import (
    detectar_saque,
    detectar_colocador,
    detectar_ataque,
    detectar_recibo,
    detectar_bloqueo
)

# Importar la función de detección multi-persona
from multi_person_detector import run_multiperson_detection
from models.classify_pose import classify_pose

# Configurar logging para errores
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/errores.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

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
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        evaluacion_resultados = {"mensajes": ["No se detectaron puntos de referencia"], "datos": []}
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            landmarks = list(results.pose_landmarks.landmark)
            evaluacion_resultados = deteccion_func(landmarks)

        return frame, evaluacion_resultados
    except Exception as e:
        logging.error(f"Error procesando frame: {e}")
        return frame, {"mensajes": ["Error en la evaluación"], "datos": []}

from utils.config import CSV_HEADERS  # Asegúrate de tener este import si usas el archivo separado

def guardar_resultados_csv(datos, path_video, deteccion):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/"""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)  # Crear la carpeta si no existe

    # Extraer el nombre base del video
    nombre_video = os.path.splitext(os.path.basename(path_video))[0]
    filename = os.path.join(carpeta_salida, f"{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        # Obtener los encabezados desde el diccionario global
        encabezados = CSV_HEADERS.get(deteccion, ["Frame", "Mensajes"])

        # Verificar si hay datos para guardar
        if not datos:
            print("No hay datos para guardar en el CSV.")
            return

        # Crear el DataFrame con los datos y encabezados
        df = pd.DataFrame(datos, columns=encabezados)
        df.to_csv(filename, index=False)
        print(f"Resultados guardados en: {filename}")
    except Exception as e:
        logging.error(f"Error al guardar el archivo CSV: {e}")
        print("No se pudieron guardar los resultados.")

def procesar_video(video_path, deteccion_func, deteccion, output_path):
    """Procesa el video frame por frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        return

    # Configuración para guardar el video procesado
    try:
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
    """Procesa el video en tiempo real desde la cámara y guarda resultados."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20  # Estimado para cámara en vivo

    os.makedirs("Salidas", exist_ok=True)
    nombre_archivo = f"camara_{deteccion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    output_path = os.path.join("Salidas", nombre_archivo)

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

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

            # Mostrar el video
            cv2.imshow("Detección en Tiempo Real", frame)

            # Guardar el frame
            out.write(frame)

            # Guardar datos
            datos_resultados.append([frame_number, *evaluacion_resultados["datos"]])

            # Salir con 'q'
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

def seleccionar_deteccion():
    """Muestra una ventana para seleccionar la detección deseada."""
    def seleccionar_opcion(opcion):
        seleccion.set(opcion)
        root.destroy()

    root = Tk()
    root.title("Seleccionar Detección")

    label = Label(root, text="Seleccione la detección que desea realizar:")
    label.pack(pady=10)

    opciones = {
        "Saque": "saque",
        "Colocador": "colocador",
        "Ataque": "ataque",
        "Recibo": "recibo",
        "Bloqueo": "bloqueo",
        "Multi Persona": "multi_persona" # Añadida la opción multi-persona
    }

    seleccion = StringVar()
    for texto, valor in opciones.items():
        boton = Button(root, text=texto, command=lambda v=valor: seleccionar_opcion(v))
        boton.pack(pady=5)

    root.mainloop()
    return seleccion.get()

def seleccionar_fuente_video():
    """Muestra una ventana para seleccionar la fuente de video (archivo o cámara)."""
    def usar_video():
        seleccion.set("video")
        root.destroy()

    def usar_camara():
        seleccion.set("camara")
        root.destroy()

    root = Tk()
    root.title("Seleccionar Fuente de Video")

    label = Label(root, text="Seleccione la fuente de video:")
    label.pack(pady=10)

    boton_video = Button(root, text="Subir Video", command=usar_video)
    boton_video.pack(pady=5)

    boton_camara = Button(root, text="Usar Cámara", command=usar_camara)
    boton_camara.pack(pady=5)

    seleccion = StringVar()
    root.mainloop()
    return seleccion.get()

def obtener_fuente_video():
    """
    Permite al usuario seleccionar la fuente de video (archivo o cámara).
    Retorna un objeto cv2.VideoCapture o una ruta de archivo.
    """
    fuente = seleccionar_fuente_video()
    if fuente == "video":
        video_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi")])
        if not video_path:
            print("No se seleccionó ningún archivo de video. Saliendo...")
            return None
        return video_path  # Retornar la ruta del archivo
    elif fuente == "camara":
        return cv2.VideoCapture(0)  # Retornar el objeto de captura de la cámara
    else:
        print("No se seleccionó ninguna fuente de video. Saliendo...")
        return None

def seleccionar_modalidad():
    """
    Muestra una ventana para seleccionar la modalidad: 'Persona' o 'Equipo'.
    Retorna la opción seleccionada como cadena.
    """
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

def seleccionar_guardar_video():
    """
    Muestra una ventana para preguntar si se desea guardar el video procesado con overlay.
    Retorna True si se elige 'Sí', o False si se elige 'No'.
    """
    seleccion = StringVar()

    def seleccionar(opcion):
        seleccion.set(opcion)
        root.destroy()

    root = Tk()
    root.title("Guardar Video Procesado")
    label = Label(root, text="¿Desea guardar el video procesado con overlay?")
    label.pack(pady=10)
    boton_si = Button(root, text="Sí", command=lambda: seleccionar("si"))
    boton_si.pack(pady=5)
    boton_no = Button(root, text="No", command=lambda: seleccionar("no"))
    boton_no.pack(pady=5)
    root.mainloop()

    return seleccion.get() == "si"

def iniciar_procesamiento():
    """Inicia el flujo principal del programa."""
    # Seleccionar modalidad mediante botones
    modalidad = seleccionar_modalidad()
    if not modalidad:
        print("No se seleccionó modalidad. Saliendo...")
        return

    if modalidad == "persona":
        # Seleccionar detección mediante ventana (ya implementada)
        deteccion = seleccionar_deteccion()
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

        # Obtener la fuente de video mediante ventana de botones
        fuente = obtener_fuente_video()
        if fuente is None:
            return

        if isinstance(fuente, str):  # Si es una ruta de archivo
            # Preguntar si se desea guardar el video procesado con overlay
            if seleccionar_guardar_video():
                nombre_video = os.path.splitext(os.path.basename(fuente))[0]
                output_path = os.path.join("Salidas", f"{deteccion}_{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
                procesar_video(fuente, deteccion_func, deteccion, output_path)
            else:
                # Procesar video sin guardar overlay (se muestran y procesan los frames)
                procesar_video_sin_guardar(fuente, deteccion_func, deteccion)
        else:  # Si es un objeto cv2.VideoCapture (cámara en tiempo real)
            procesar_video_camara(deteccion_func, deteccion)

    elif modalidad == "equipo":
        # Para análisis de equipo, seleccionar directamente la fuente (ventana con botones)
        fuente = obtener_fuente_video()
        if fuente is None:
            return

        if isinstance(fuente, str):  # Si es una ruta de archivo
            print(f"Iniciando detección multipersona en el video: {fuente}")
            run_multiperson_detection(video_path=fuente)
        else:  # Si es un objeto cv2.VideoCapture (cámara)
            print("Iniciando detección multipersona en tiempo real desde la cámara...")
            run_multiperson_detection()

    else:
        print("Opción no válida. Saliendo...")

# Ejemplo de función de procesamiento sin guardar el video (se muestra overlay pero no se guarda)
def procesar_video_sin_guardar(video_path, deteccion_func, deteccion):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("No se pudo abrir el video.")
        return

    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame, evaluacion_resultados = procesar_frame(frame, pose, deteccion_func, frame_number)
        cv2.imshow("Detección en Tiempo Real", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_number += 1

    cap.release()
    cv2.destroyAllWindows()
    print("Procesamiento en tiempo real finalizado (video no guardado).")

if __name__ == "__main__":
    iniciar_procesamiento()
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

def guardar_resultados_csv(datos, path_video, deteccion):
    """Guarda los datos de evaluación en un archivo CSV dentro de la carpeta Salidas/"""
    carpeta_salida = "Salidas"
    os.makedirs(carpeta_salida, exist_ok=True)  # Crear la carpeta si no existe

    # Extraer el nombre base del video
    nombre_video = os.path.splitext(os.path.basename(path_video))[0]
    filename = os.path.join(carpeta_salida, f"{nombre_video}_procesado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    try:
        # Ajustar los encabezados y datos según la detección seleccionada
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
        logging.error(f"Error en el procesamiento de la cámara: {e}")
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
        "Bloqueo": "bloqueo"
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

def iniciar_procesamiento():
    """Inicia el flujo principal del programa."""
    # Seleccionar la detección
    deteccion = seleccionar_deteccion()
    if not deteccion:
        print("No se seleccionó ninguna detección. Saliendo...")
        return

    # Mapear la detección seleccionada a la función correspondiente
    opciones = {
        "saque": detectar_saque,
        "colocador": detectar_colocador,
        "ataque": detectar_ataque,
        "recibo": detectar_recibo,
        "bloqueo": detectar_bloqueo
    }
    deteccion_func = opciones.get(deteccion)
    if not deteccion_func:
        print("Detección no válida seleccionada. Saliendo...")
        return

    # Seleccionar la fuente de video
    fuente = seleccionar_fuente_video()
    if fuente == "video":
        video_path = filedialog.askopenfilename(filetypes=[("Archivos de video", "*.mp4;*.avi")])
        if not video_path:
            print("No se seleccionó ningún archivo de video. Saliendo...")
            return
        nombre_video = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join("Salidas", f"{deteccion}_{nombre_video}_procesado.mp4")
        procesar_video(video_path, deteccion_func, deteccion, output_path)
    elif fuente == "camara":
        procesar_video_camara(deteccion_func, deteccion)
    else:
        print("No se seleccionó ninguna fuente de video. Saliendo...")

if __name__ == "__main__":
    iniciar_procesamiento()

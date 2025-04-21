def run_multiperson_detection(video_path=None):
    """
    Realiza detección multipersona en tiempo real desde la cámara o un video pregrabado.
    
    Parámetros:
        video_path (str, opcional): Ruta del archivo de video. Si es None, se usará la cámara.
    """
    import cv2
    import numpy as np
    import pandas as pd
    from collections import deque
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode, ImageFormat
    from mediapipe.tasks.python.vision import Image as mpImage
    from mediapipe import solutions
    from models.classify_pose import classify_pose  # Importamos la función desde models
    import time
    import uuid  # Para generar IDs únicos

    global pose_id_counter  # Declaración global al inicio de la función
    pose_id_counter = 0

    # Inicialización del landmarker multipersona
    options = PoseLandmarkerOptions(
        base_options=mp_tasks.BaseOptions(model_asset_path='models/pose_landmarker_full.task'),
        running_mode=RunningMode.LIVE_STREAM,
        num_poses=6  # Detectar hasta 6 personas
    )
    landmarker = PoseLandmarker.create_from_options(options)

    # Inicializar las utilidades de dibujo de MediaPipe
    mp_drawing = solutions.drawing_utils
    mp_pose = solutions.pose

    # Captura de video (cámara o archivo)
    if video_path:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"No se pudo abrir el archivo de video: {video_path}")
            return
    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("No se pudo acceder a la cámara.")
            return

    pose_history = {}  # Historial de poses por persona (por ID)
    tracked_poses = {}  # Poses rastreadas en el frame actual con sus IDs
    previous_poses = {}  # Poses detectadas en el frame anterior con sus IDs
    distance_threshold = 0.2  # Umbral para considerar dos poses como la misma persona
    max_frames = 30  # Número de frames a considerar para promediar keypoints
    font = cv2.FONT_HERSHEY_SIMPLEX  # Fuente para mostrar texto en pantalla
    timestamp = 0  # Timestamp inicial para los frames en streaming
    data_to_save = []  # Para almacenar los resultados con IDs

    def calcular_distancia_poses(pose1, pose2):
        """Calcula la distancia euclidiana promedio entre los keypoints de dos poses."""
        total_distance = 0
        num_landmarks = len(pose1.landmark)
        for i in range(num_landmarks):
            dx = pose1.landmark[i].x - pose2.landmark[i].x
            dy = pose1.landmark[i].y - pose2.landmark[i].y
            dz = pose1.landmark[i].z - pose2.landmark[i].z
            total_distance += np.sqrt(dx**2 + dy**2 + dz**2)
        return total_distance / num_landmarks if num_landmarks > 0 else float('inf')

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("No se pudo leer el frame.")
            break

        # Incrementar timestamp según fps
        timestamp += int(1000 / cap.get(cv2.CAP_PROP_FPS))

        # Convertir el frame a imagen compatible con MediaPipe
        mp_image = mpImage(image_format=ImageFormat.SRGB, data=frame)

        # Realizar la detección asincrónica
        result = landmarker.detect(mp_image)

        tracked_poses = {}  # Reiniciar las poses rastreadas en este frame
        current_detected_poses = result.pose_landmarks if result.pose_landmarks else []

        # Lógica de seguimiento
        if previous_poses:
            assigned_ids = set()
            new_tracked_poses = {}
            for i, current_pose in enumerate(current_detected_poses):
                min_distance = float('inf')
                matched_id = None
                for prev_id, prev_pose in previous_poses.items():
                    distance = calcular_distancia_poses(current_pose, prev_pose)
                    if distance < min_distance and prev_id not in assigned_ids:
                        min_distance = distance
                        matched_id = prev_id

                if matched_id and min_distance < distance_threshold:
                    new_tracked_poses[matched_id] = current_pose
                    assigned_ids.add(matched_id)
                else:
                    new_id = f"person_{pose_id_counter}"
                    new_tracked_poses[new_id] = current_pose
                    pose_id_counter += 1
            tracked_poses = new_tracked_poses
        else:
            # Si es el primer frame, asignar IDs iniciales
            for i, pose in enumerate(current_detected_poses):
                tracked_poses[f"person_{i}"] = pose
                pose_id_counter = max(pose_id_counter, i + 1)

        previous_poses = tracked_poses.copy()  # Actualizar las poses previas para el siguiente frame

        # Procesar y dibujar las poses rastreadas
        for person_id, landmarks in tracked_poses.items():
            # Dibujar los landmarks y las conexiones
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

            # Obtener keypoints como array plano
            keypoints = [(lm.x, lm.y, lm.z) for lm in landmarks.landmark]
            keypoints_array = np.array(keypoints).flatten()

            # Inicializar historial para la persona rastreada
            if person_id not in pose_history:
                pose_history[person_id] = deque(maxlen=max_frames)

            # Añadir keypoints actuales al historial
            pose_history[person_id].append(keypoints_array)

            # Si hay suficientes frames acumulados
            if len(pose_history[person_id]) == max_frames:
                # Promediar keypoints
                avg_keypoints = np.mean(pose_history[person_id], axis=0)

                # Clasificar acción
                action_label = classify_pose(avg_keypoints)

                # Mostrar la etiqueta con el ID
                cv2.putText(frame, f'{person_id}: {action_label}',
                            (50, 50 + list(tracked_poses.keys()).index(person_id) * 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # Guardar resultado con el ID
                data_to_save.append({
                    'persona_id': person_id,
                    'accion': action_label
                })
            else:
                # Mostrar solo el ID mientras se acumulan frames
                cv2.putText(frame, f'{person_id}',
                            (50, 50 + list(tracked_poses.keys()).index(person_id) * 30), font, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # Mostrar el frame
        cv2.imshow('Detección de acciones - Voleibol', frame)

        # Salir al presionar 'ESC'
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

    # Guardar resultados con IDs
    df = pd.DataFrame(data_to_save)
    df.to_csv('Salidas/acciones_detectadas_con_ids.csv', index=False)
    print("Resultados guardados en 'Salidas/acciones_detectadas_con_ids.csv'.")

if __name__ == '__main__':
    run_multiperson_detection()
import os
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from collections import deque
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe import Image, ImageFormat
from mediapipe import solutions
import time


class MultiPersonDetector:
    """
    Clase para realizar detección multipersona utilizando MediaPipe.
    Permite procesar videos o la cámara en tiempo real, guardar los resultados en un archivo CSV
    y generar un video procesado con las poses detectadas.
    """

    def __init__(self, model_path='models/pose_landmarker_heavy.task', output_dir="Salidas"):
        """
        Inicializa el detector multipersona.

        Args:
            model_path (str): Ruta al modelo de MediaPipe (.task).
            output_dir (str): Carpeta donde se guardarán los resultados (CSV y video).
        """
        self.model_path = model_path
        self.output_dir = output_dir
        self.pose_id_counter = 0
        self.tracked_poses = {}
        self.previous_poses = {}
        self.pose_history = deque(maxlen=50)
        self.data_to_save = []
        self.distance_threshold = 0.2

        # Crear la carpeta de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)

        # Inicializar el landmarker
        options = PoseLandmarkerOptions(
            base_options=mp_tasks.BaseOptions(model_asset_path=self.model_path),
            running_mode=RunningMode.LIVE_STREAM,
            num_poses=6,
            result_callback=self.on_results
        )
        self.landmarker = PoseLandmarker.create_from_options(options)

    def calcular_distancia_poses(self, pose1, pose2):
        """
        Calcula la distancia euclidiana promedio entre los keypoints de dos poses.

        Args:
            pose1: Pose actual (MediaPipe pose_landmarks).
            pose2: Pose previa (MediaPipe pose_landmarks).

        Returns:
            float: Distancia promedio entre los keypoints de las dos poses.
        """
        total_distance = 0
        num_landmarks = len(pose1.landmark)

        for i in range(num_landmarks):
            dx = pose1.landmark[i].x - pose2.landmark[i].x
            dy = pose1.landmark[i].y - pose2.landmark[i].y
            dz = pose1.landmark[i].z - pose2.landmark[i].z
            total_distance += (dx**2 + dy**2 + dz**2)**0.5

        return total_distance / num_landmarks if num_landmarks > 0 else float('inf')

    def on_results(self, result, output_timestamp_ms):
        """
        Callback para manejar los resultados de detección.

        Args:
            result: Resultado de detección proporcionado por MediaPipe.
            output_timestamp_ms (int): Timestamp del frame procesado en milisegundos.
        """
        current_detected_poses = result.pose_landmarks if result.pose_landmarks else []
        self.tracked_poses = {}

        if self.previous_poses:
            assigned_ids = set()
            new_tracked_poses = {}
            for current_pose in current_detected_poses:
                min_distance = float('inf')
                matched_id = None
                for prev_id, prev_pose in self.previous_poses.items():
                    distance = self.calcular_distancia_poses(current_pose, prev_pose)
                    if distance < min_distance and prev_id not in assigned_ids:
                        min_distance = distance
                        matched_id = prev_id

                if matched_id and min_distance < self.distance_threshold:
                    new_tracked_poses[matched_id] = current_pose
                    assigned_ids.add(matched_id)
                else:
                    new_id = f"person_{self.pose_id_counter}"
                    new_tracked_poses[new_id] = current_pose
                    self.pose_id_counter += 1
            self.tracked_poses = new_tracked_poses
        else:
            for i, pose in enumerate(current_detected_poses):
                self.tracked_poses[f"person_{self.pose_id_counter}"] = pose
                self.pose_id_counter += 1

        self.previous_poses = self.tracked_poses.copy()

        # Guardar datos de los landmarks en data_to_save
        for person_id, pose_landmarks in self.tracked_poses.items():
            for idx, landmark in enumerate(pose_landmarks.landmark):
                self.data_to_save.append({
                    "person_id": person_id,
                    "timestamp": output_timestamp_ms,
                    "landmark_index": idx,
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                })

    def process_video(self, video_path=None):
        """
        Procesa un video o la cámara en tiempo real.

        Args:
            video_path (str, optional): Ruta al video a procesar. Si es None, se utiliza la cámara.
        """
        cap = cv2.VideoCapture(0 if video_path is None else video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        output_filename = os.path.join(self.output_dir, f"processed_video_{time.strftime('%Y%m%d_%H%M%S')}.avi")
        out = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

        start_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            timestamp_ms = int((time.time() - start_time) * 1000)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)
            self.landmarker.detect_async(mp_image, timestamp_ms)

            for idx, (person_id, pose_landmarks) in enumerate(self.tracked_poses.items()):
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    pose_landmarks,
                    mp.solutions.pose.POSE_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_pose_landmarks_style()
                )
                cv2.putText(frame, f"ID: {person_id}", (10, 30 + 30 * idx), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            out.write(frame)
            cv2.imshow("DballTrainer Multiperson Detector", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Guardar los datos en un archivo CSV
        df = pd.DataFrame(self.data_to_save)
        filename = os.path.join(self.output_dir, f"pose_data_{time.strftime('%Y%m%d_%H%M%S')}.csv")
        df.to_csv(filename, index=False)
        print(f"Datos guardados en el archivo: {filename}")
        print(f"Video procesado guardado en: {output_filename}")

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def close(self):
        """
        Libera los recursos del landmarker.
        """
        self.landmarker.close()


if __name__ == '__main__':
    detector = MultiPersonDetector()
    detector.process_video("ruta_del_video.mp4")  # Cambia por la ruta de tu video
    detector.close()

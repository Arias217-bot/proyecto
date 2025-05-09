from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
import requests
import traceback

analisis_bp = Blueprint('analisis', __name__)

# Configuración
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
# Configuración con ruta relativa
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'analisis_videos')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@analisis_bp.route('/video/<tipo_deteccion>', methods=['POST'])
def analizar_video(tipo_deteccion):
    try:
        # 1. Validar archivo recibido
        if 'video' not in request.files:
            return jsonify({"error": "No se envió video"}), 400
            
        file = request.files['video']
        if file.filename == '':
            return jsonify({"error": "Nombre de archivo inválido"}), 400

        # 2. Enviar al backend de análisis
        api_url = f"{current_app.config['ANALISIS_API_URL']}/analizar_video/{tipo_deteccion}"
        response = requests.post(
            api_url,
            files={'video': (file.filename, file.stream, file.mimetype)},
            timeout=120  # 2 minutos para análisis largo
        )
        
        # 3. Manejar respuesta
        if response.status_code != 200:
            return jsonify({
                "error": f"Error en el backend: {response.text}",
                "status_code": response.status_code
            }), 502
            
        return jsonify(response.json())

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Error de conexión: {str(e)}",
            "solucion": "Verifica que el backend esté corriendo"
        }), 503
    except Exception as e:
        current_app.logger.error(f"Error inesperado: {traceback.format_exc()}")
        return jsonify({
            "error": "Error interno del servidor",
            "detalle": str(e)
        }), 500
       
def analizar_video_externo(video_path, accion):
    ANALISIS_API_URL = "http://backend-analisis.example.com"  # Configurar en variables de entorno
    
    with open(video_path, 'rb') as f:
        response = requests.post(
            f"{ANALISIS_API_URL}/analizar_video/{accion}",
            files={'video': f},
            timeout=300  # 5 minutos para análisis largo
        )
    
    if response.status_code != 200:
        raise Exception(response.json().get('error', 'Error en el servicio de análisis'))
    
    return response.json()

def analizar_video_externo(video_path, accion):
    api_url = current_app.config['ANALISIS_API_URL']
    
    response = requests.post(
        f"{api_url}/analizar_video/{accion}",
        files={'video': open(video_path, 'rb')}
    )
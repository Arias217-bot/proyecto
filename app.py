from flask import Flask, request, jsonify, make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS
import shutil
import os
import uuid
from integration import analizar_video, analizar_camara, funciones_deteccion
from typing import Optional
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de la aplicación
app.config['TITLE'] = "API de Análisis de Voleibol"
app.config['DESCRIPTION'] = "API para detectar acciones específicas de voleibol en videos o en tiempo real"
app.config['VERSION'] = "1.0"
app.config['UPLOAD_DIR'] = "uploads"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB límite para videos

# Crear directorio de uploads si no existe
os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)


@app.route("/analizar", methods=["POST", "GET"])
def analizar():
    """
    Ruta unificada para:
    - GET: acciones disponibles
    - POST: analizar archivo (con o sin jugador_id) o por cámara
    """
    if request.method == "GET":
        return jsonify({"acciones_disponibles": list(funciones_deteccion.keys())})

    # POST: analizar video o cámara
    modo = request.form.get('modo', 'archivo')  # valores posibles: archivo, jugador, camara
    deteccion = request.form.get('deteccion') or request.args.get('deteccion')
    jugador_id = request.form.get('jugador_id')  # solo para modo jugador

    if not deteccion or deteccion not in funciones_deteccion:
        return jsonify({"error": f"'{deteccion}' no es una detección válida"}), 400

    try:
        if modo == "camara":
            resultados = analizar_camara(deteccion)
            return jsonify({
                "status": "success",
                "analisis": resultados,
                "metadata": {
                    "modo": "tiempo_real",
                    "accion_analizada": deteccion
                }
            })

        if 'archivo' not in request.files:
            return jsonify({"error": "No se proporcionó archivo de video"}), 400

        archivo = request.files['archivo']
        extension = secure_filename(archivo.filename).split(".")[-1]
        nombre_archivo = f"{uuid.uuid4()}.{extension}"
        ruta_archivo = os.path.join(app.config['UPLOAD_DIR'], nombre_archivo)
        archivo.save(ruta_archivo)

        resultados = analizar_video(ruta_archivo, deteccion)

        os.remove(ruta_archivo)

        respuesta = {
            "status": "success",
            "analisis": resultados,
            "metadata": {
                "modelo": "MediaPipe + TensorFlow Lite",
                "accion_analizada": deteccion
            }
        }

        if modo == "jugador":
            respuesta["jugador_id"] = jugador_id
            respuesta["metadata"].update({
                "sistema": "Flask MediaPipe",
                "version": app.config.get('VERSION', '1.0')
            })

        return jsonify(respuesta)

    except Exception as e:
        error_msg = {"error": f"Error en el análisis: {str(e)}"}
        if modo == "jugador":
            error_msg["jugador_id"] = jugador_id
        return jsonify(error_msg), 500

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "mensaje": "API de análisis de acciones de voleibol (una persona) usando MediaPipe",
        "integracion": {
            "flask_endpoint": "/analizar/video/jugador/",
            "parametros": {
                "archivo": "Video file",
                "deteccion": f"Acciones disponibles: {list(funciones_deteccion.keys())}",
                "jugador_id": "ID opcional del jugador"
            }
        }
    })

@app.route("/healthcheck", methods=["GET"])
def health_check():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({
        "status": "ok",
        "service": "Volleyball Action Analysis API",
        "version": app.config['VERSION'],
        "dependencies": {
            "mediapipe": "active",
            "tensorflow": "active"
        }
    })

@app.route("/acciones/", methods=["GET"])
def obtener_acciones():
    """Devuelve las acciones disponibles para detección."""
    return jsonify({"acciones_disponibles": list(funciones_deteccion.keys())})

@app.route("/analizar/video/", methods=["POST"])
def analizar_archivo_video():
    """
    Endpoint para analizar un archivo de video subido.
    """
    if 'archivo' not in request.files:
        return jsonify({"error": "No se proporcionó archivo de video"}), 400
    
    archivo = request.files['archivo']
    deteccion = request.form.get('deteccion')
    
    if not deteccion or deteccion not in funciones_deteccion:
        return jsonify({"error": f"'{deteccion}' no es una detección válida"}), 400

    try:
        # Guardar archivo temporalmente
        extension = secure_filename(archivo.filename).split(".")[-1]
        nombre_archivo = f"{uuid.uuid4()}.{extension}"
        ruta_archivo = os.path.join(app.config['UPLOAD_DIR'], nombre_archivo)

        archivo.save(ruta_archivo)

        # Ejecutar análisis
        resultados = analizar_video(ruta_archivo, deteccion)

        # Eliminar archivo después del análisis
        os.remove(ruta_archivo)

        return jsonify({
            "status": "success",
            "analisis": resultados,
            "metadata": {
                "modelo": "MediaPipe + TensorFlow Lite",
                "accion_analizada": deteccion
            }
        })

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route("/analizar/video/jugador/", methods=["POST"])
def analizar_video_jugador():
    """
    Endpoint especial para integración con sistemas externos.
    Incluye identificación de jugador para correlacionar con bases de datos.
    """
    if 'archivo' not in request.files:
        return jsonify({"error": "No se proporcionó archivo de video"}), 400
    
    archivo = request.files['archivo']
    deteccion = request.form.get('deteccion')
    jugador_id = request.form.get('jugador_id')

    if not deteccion or deteccion not in funciones_deteccion:
        return jsonify({"error": f"'{deteccion}' no es una detección válida"}), 400

    try:
        # Guardar archivo temporalmente
        extension = secure_filename(archivo.filename).split(".")[-1]
        nombre_archivo = f"{uuid.uuid4()}.{extension}"
        ruta_archivo = os.path.join(app.config['UPLOAD_DIR'], nombre_archivo)

        archivo.save(ruta_archivo)

        # Ejecutar análisis
        resultados = analizar_video(ruta_archivo, deteccion)

        # Eliminar archivo después del análisis
        os.remove(ruta_archivo)

        return jsonify({
            "status": "success",
            "jugador_id": jugador_id,
            "analisis": resultados,
            "metadata": {
                "modelo": "MediaPipe + TensorFlow Lite",
                "accion_analizada": deteccion,
                "sistema": "Flask MediaPipe",
                "version": app.config['VERSION']
            }
        })

    except Exception as e:
        return jsonify({
            "error": f"Error en el análisis: {str(e)}",
            "jugador_id": jugador_id
        }), 500

@app.route("/analizar/camara/", methods=["GET"])
def analizar_desde_camara():
    """
    Endpoint para analizar en tiempo real desde cámara web.
    """
    deteccion = request.args.get('deteccion')
    
    if not deteccion or deteccion not in funciones_deteccion:
        return jsonify({"error": f"'{deteccion}' no es una detección válida"}), 400

    try:
        resultados = analizar_camara(deteccion)
        return jsonify({
            "status": "success",
            "analisis": resultados,
            "metadata": {
                "modo": "tiempo_real",
                "accion_analizada": deteccion
            }
        })
    except Exception as e:
        return jsonify({"error": f"Error en cámara: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
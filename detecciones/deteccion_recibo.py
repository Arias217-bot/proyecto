import math
import logging
from mediapipe.python.solutions.pose import PoseLandmark
from evaluaciones.evaluar_sentadillas import evaluar_sentadillas
from evaluaciones.evaluar_contacto import evaluar_contacto
from evaluaciones.evaluar_posicion import evaluar_posicion
from evaluaciones.evaluar_movimiento import evaluar_movimiento
from evaluaciones.evaluar_estabilidad import evaluar_estabilidad

logging.basicConfig(level=logging.ERROR)

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos en 2D."""
    if not all(hasattr(p, 'x') and hasattr(p, 'y') for p in [p1, p2, p3]):
        logging.error("Todos los puntos deben tener atributos 'x' y 'y'.")
        return None

    angulo = math.degrees(
        math.atan2(p3.y - p2.y, p3.x - p2.x) - 
        math.atan2(p1.y - p2.y, p1.x - p2.x)
    )
    return abs(angulo) if angulo >= 0 else abs(angulo + 360)

def detectar_recibo(landmarks):
    """Detecta la postura de recibo basado en los puntos de referencia del cuerpo en voleibol."""
    try:
        # Validar landmarks
        if not isinstance(landmarks, list) or len(landmarks) < 33:
            logging.error("La lista de landmarks es inválida o incompleta.")
            return {"mensajes": ["Error: datos insuficientes para evaluar recibo"], "datos": {}}

        # Landmarks clave
        cadera = landmarks[PoseLandmark.LEFT_HIP.value]
        rodilla = landmarks[PoseLandmark.LEFT_KNEE.value]
        tobillo = landmarks[PoseLandmark.LEFT_ANKLE.value]
        hombro = landmarks[PoseLandmark.LEFT_SHOULDER.value]
        cabeza = landmarks[PoseLandmark.NOSE.value]
        manos = [landmarks[PoseLandmark.LEFT_WRIST.value], landmarks[PoseLandmark.RIGHT_WRIST.value]]

        # Cálculo de ángulos
        angulo_tronco = calcular_angulo(cadera, hombro, cabeza)
        profundidad_sentadilla = calcular_angulo(cadera, rodilla, tobillo)

        # Validación de ángulos
        if angulo_tronco is None or profundidad_sentadilla is None:
            logging.error("No se pudieron calcular algunos ángulos.")
            return {"mensajes": ["Error en los cálculos de ángulos"], "datos": {}}

        # Evaluaciones
        posicion_correcta = evaluar_posicion(landmarks)
        contacto_brazos = evaluar_contacto(manos)
        estabilidad = evaluar_estabilidad(landmarks)  # Mejor pasar todos los puntos
        sentadilla_correcta = evaluar_sentadillas(profundidad_sentadilla)
        movimiento_excesivo = evaluar_movimiento(landmarks)  # Se podría analizar en secuencia

        # Resultados finales con mensajes más explicativos
        resultados = []

        if 70 <= angulo_tronco <= 110:
            resultados.append("✅ Ángulo del tronco dentro del rango adecuado.")
        else:
            resultados.append("⚠️ Ajustar inclinación del tronco para mejorar estabilidad.")

        if sentadilla_correcta:
            resultados.append("✅ Profundidad de sentadilla correcta para absorción del impacto.")
        else:
            resultados.append("⚠️ Ajustar la flexión de rodillas para mayor control.")

        if posicion_correcta:
            resultados.append("✅ Posición corporal adecuada para recibir el balón.")
        else:
            resultados.append("⚠️ Ajustar la postura general para optimizar el recibo.")

        if contacto_brazos:
            resultados.append("✅ Contacto con el balón correcto.")
        else:
            resultados.append("⚠️ Ajustar posición de los brazos para mejorar contacto.")

        if estabilidad:
            resultados.append("✅ Postura estable al momento del contacto.")
        else:
            resultados.append("⚠️ Mejorar el balance y la posición de los pies.")

        if not movimiento_excesivo:
            resultados.append("✅ Movimiento controlado durante el recibo.")
        else:
            resultados.append("⚠️ Reducir movimientos innecesarios que pueden afectar el control.")

        return {
            "mensajes": resultados,
            "datos": {
                "angulo_tronco": angulo_tronco,
                "profundidad_sentadilla": profundidad_sentadilla,
                "posicion_correcta": posicion_correcta,
                "contacto_brazos": contacto_brazos,
                "estabilidad": estabilidad,
                "movimiento_excesivo": movimiento_excesivo
            }
        }

    except Exception as e:
        logging.error(f"Error en detectar_recibo: {e}", exc_info=True)
        return {"mensajes": ["❌ Error en la detección del recibo"], "datos": {}}
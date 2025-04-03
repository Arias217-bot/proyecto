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

        # Evaluaciones
        posicion_correcta = evaluar_posicion(landmarks)
        contacto_brazos = evaluar_contacto(manos)
        estabilidad = evaluar_estabilidad(cadera, tobillo)
        sentadilla_correcta = evaluar_sentadillas(profundidad_sentadilla)
        movimiento_excesivo = evaluar_movimiento(landmarks)

        if angulo_tronco is None or profundidad_sentadilla is None:
            logging.error("No se pudieron calcular algunos ángulos.")
            return {"mensajes": ["Error en los cálculos de ángulos"], "datos": {}}

        # Resultados finales
        resultados = [
            "Ángulo del tronco correcto" if 70 <= angulo_tronco <= 110 else "Ajustar ángulo del tronco",
            "Profundidad de sentadilla correcta" if sentadilla_correcta else "Ajustar profundidad de sentadilla",
            "Posición corporal correcta" if posicion_correcta else "Ajustar posición",
            "Contacto de balón correcto" if contacto_brazos else "Ajustar contacto de brazos",
            "Estabilidad correcta" if estabilidad else "Ajustar estabilidad",
            "Movimiento controlado" if not movimiento_excesivo else "Reducir movimiento innecesario"
        ]

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
        return {"mensajes": ["Error en la detección de recibo"], "datos": {}}
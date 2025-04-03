import math
import mediapipe as mp

mp_pose = mp.solutions.pose

def calcular_angulo(p1, p2, p3):
    """Calcula el ángulo entre tres puntos."""
    try:
        angulo = math.degrees(
            math.atan2(p3.y - p2.y, p3.x - p2.x) - 
            math.atan2(p1.y - p2.y, p1.x - p2.x)
        )
        return abs(angulo) if angulo >= 0 else abs(angulo + 360)
    except Exception as e:
        print(f"Error al calcular el ángulo: {e}")
        return None

def detectar_bloqueo(landmarks):
    """
    Detecta y evalúa la técnica de bloqueo en voleibol.
    Args:
        landmarks (list): Lista de landmarks detectados por MediaPipe.
    Returns:
        dict: Resultados de la detección con mensajes y datos relevantes.
    """
    try:
        # Verificar que los landmarks necesarios existen
        puntos_requeridos = [
            mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST,
            mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST,
            mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP
        ]

        if any(landmarks[p.value] is None for p in puntos_requeridos):
            return {"mensajes": ["❌ Faltan landmarks para evaluar el bloqueo."], "datos": []}

        # Extraer landmarks relevantes
        hombro_izq = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        codo_izq = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        muñeca_izq = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

        hombro_der = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        codo_der = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        muñeca_der = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

        cabeza = landmarks[mp_pose.PoseLandmark.NOSE.value]
        cadera_izq = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        cadera_der = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        # Calcular ángulos de los brazos
        angulo_brazos_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulo_brazos_der = calcular_angulo(hombro_der, codo_der, muñeca_der)

        # Altura del bloqueo (normalizada con la cabeza como referencia)
        altura_bloqueo_izq = muñeca_izq.y / cabeza.y
        altura_bloqueo_der = muñeca_der.y / cabeza.y

        # Calcular alineación del tronco (hombros con respecto a las caderas)
        angulo_tronco = calcular_angulo(cadera_izq, hombro_izq, hombro_der)

        # Verificar que los valores sean válidos
        if None in [angulo_brazos_izq, angulo_brazos_der, altura_bloqueo_izq, altura_bloqueo_der, angulo_tronco]:
            return {"mensajes": ["❌ No se pudieron calcular algunos valores."], "datos": []}

        # Criterios de bloqueo válido
        bloqueo_valido_izq = angulo_brazos_izq > 160 and altura_bloqueo_izq < 0.5
        bloqueo_valido_der = angulo_brazos_der > 160 and altura_bloqueo_der < 0.5
        tronco_alineado = 75 <= angulo_tronco <= 105

        bloqueo_valido = bloqueo_valido_izq and bloqueo_valido_der and tronco_alineado

        # Mensajes descriptivos
        mensajes = [
            f"Ángulo brazo izquierdo: {angulo_brazos_izq:.2f}° {'✅' if angulo_brazos_izq > 160 else '❌'}",
            f"Ángulo brazo derecho: {angulo_brazos_der:.2f}° {'✅' if angulo_brazos_der > 160 else '❌'}",
            f"Altura muñeca izquierda: {'✅ Correcta' if altura_bloqueo_izq < 0.5 else '❌ Demasiado baja'}",
            f"Altura muñeca derecha: {'✅ Correcta' if altura_bloqueo_der < 0.5 else '❌ Demasiado baja'}",
            f"Tronco {'✅ Alineado' if tronco_alineado else '❌ Desalineado'}",
            f"Bloqueo {'✅ Válido' if bloqueo_valido else '❌ No válido'}"
        ]

        # Datos para análisis
        datos = {
            "angulo_brazos_izq": angulo_brazos_izq,
            "angulo_brazos_der": angulo_brazos_der,
            "altura_bloqueo_izq": altura_bloqueo_izq,
            "altura_bloqueo_der": altura_bloqueo_der,
            "angulo_tronco": angulo_tronco,
            "bloqueo_valido": bloqueo_valido
        }

        return {"mensajes": mensajes, "datos": datos}

    except Exception as e:
        print(f"Error en detectar_bloqueo: {e}")
        return {"mensajes": ["❌ Error en la detección de bloqueo"], "datos": []}

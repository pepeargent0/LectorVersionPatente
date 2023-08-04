import logging
import os
import threading
import time
from datetime import datetime

import cv2
import jaro
import numpy as np
import paho.mqtt.client as mqtt

from camara.rtsp import RTSPClient
from config.config import get_model_config, get_directory_config, get_database_url, get_mqtt_config
from database.database import get_session, init_sin_tunel_database
from database.empresas import Empresas
from database.transporte_egreso import TransporteEgreso
from database.habilitar_transporte_egreso import HabilitarTransporteEgreso
from database.transporte_vehiculos import TransporteVehiculos
from patentes.alpr import ALPR

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

db_url = get_database_url()
init_sin_tunel_database(db_url)
session = get_session()
username = get_mqtt_config().username
password = get_mqtt_config().password
port = int(get_mqtt_config().port)
broker = get_mqtt_config().broker
topico_semaforo = get_mqtt_config().semaforo
topico_camara = get_mqtt_config().camara
topico_barrera = get_mqtt_config().barrera

client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    client.publish(topico_semaforo, "#out1-off")
    client.publish(topico_semaforo, "#out2-on")
    time.sleep(20)
    client.publish(topico_barrera, "#out1-pulse")
    time.sleep(20)
    client.publish(topico_camara, "#combo-simple")
    time.sleep(50)
    client.publish(topico_semaforo, "#out2-off")
    client.publish(topico_semaforo, "#out1-on")



def zoom_image(image, scale_factor):
    return cv2.resize(image, None, fx=scale_factor, fy=scale_factor)


def resize_frame(frame, target_size):
    # Redimensionar la imagen al tamaño objetivo
    resized_frame = cv2.resize(frame, target_size)
    return resized_frame


def crop_frame(frame, porcentaje_recorte):
    # Calcular los márgenes recortados
    margen_recorte_ancho = int(frame.shape[1] * porcentaje_recorte)
    margen_recorte_alto = int(frame.shape[0] * porcentaje_recorte)
    # Definir las coordenadas de recorte
    x1 = margen_recorte_ancho
    y1 = margen_recorte_alto
    x2 = frame.shape[1] - margen_recorte_ancho
    y2 = frame.shape[0] - margen_recorte_alto
    # Recortar la región de interés dentro de los márgenes recortados
    cropped_frame = frame[y1:y2, x1:x2]
    return cropped_frame


def recortar_patente(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]


def process_frame(frame):
    directory_storage = get_directory_config()
    predicts = alpr.show_predicts(frame)
    if not predicts:
        return
    try:
        resultados = session.query(HabilitarTransporteEgreso).all()
        session.commit()
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    aproximado = {
        'id': '',
        'patente': '',
        'distancia_jaro': -1
    }

    distancias_jaro = [jaro.jaro_winkler_metric(resultado.patente, predicts.patente) for resultado in resultados]
    print(distancias_jaro)
    if len(distancias_jaro) > 0:
        max_distancia_jaro = max(distancias_jaro)
        if max_distancia_jaro > aproximado['distancia_jaro']:
            index_max_distancia_jaro = distancias_jaro.index(max_distancia_jaro)
            resultado_seleccionado = resultados[index_max_distancia_jaro]
            aproximado = {
                'id': resultado_seleccionado.id,
                'patente': resultado_seleccionado.patente,
                'distancia_jaro': max_distancia_jaro
            }
    if aproximado['distancia_jaro'] < 0.70:
        print('Patente No Habilitada: ', predicts.patente)
    else:
        transport_vehiculos = session.query(HabilitarTransporteEgreso).filter(
            HabilitarTransporteEgreso.id == aproximado['id']).first()

        print('patente',aproximado['patente'])
        print(transport_vehiculos)
        if transport_vehiculos:
            print(transport_vehiculos.interno_id)
            # empresa = session.query(Empresas).filter(Empresas.id == transport_vehiculos.empresa_id).first()

            try:
                egreso_veiculo = TransporteEgreso(
                    patente=aproximado['patente'],
                    procesado=True,
                    fecha_salida=datetime.now().date(),
                    hora_salida=datetime.now().time(),
                    lectura_forzada=False,
                    motivo='',
                    interno_id=transport_vehiculos.interno_id
                )
                session.add(egreso_veiculo)
                session.commit()
            except Exception as e:
                print(f"Error al ejecutar la consulta: {e}")
            print('Patente Insertado: ', aproximado['patente'], ' Patente Detectada: ', predicts.patente)
            session.delete(transport_vehiculos)
            session.commit()
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
            base_directory = directory_storage.destination + '/' + str(transport_vehiculos.interno_id)
            if not os.path.exists(base_directory):
                os.mkdir(base_directory)
            else:
                base_directory = directory_storage.destination + '/' + str(transport_vehiculos.interno_id) + '/' + str(transport_vehiculos.interno_id)
            imagen_path = os.path.join(base_directory, f'{timestamp}_patente.jpg')
            x1, y1, x2, y2 = predicts.posicion
            plate_region = recortar_patente(frame, x1, y1, x2, y2)
            zoomed_plate_region = zoom_image(plate_region, scale_factor=2.5)
            cv2.imwrite(imagen_path, zoomed_plate_region)
            imagen_path = os.path.join(base_directory, f'{timestamp}.jpg')
            cv2.imwrite(imagen_path, frame)


def capture_frames():
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    last_frame_time = time.time()
    try:
        while cap.isOpened():
            return_value, frame = cap.read()
            if not return_value:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convertir el frame a un arreglo de NumPy
            frame_np = np.array(frame)
            # Redimensionar el frame
            target_size = (848, 480)
            resized_frame = cv2.resize(frame_np, target_size)
            # Calcular los márgenes recortados
            # porcentaje_recorte = 0.10  # Porcentaje de recorte deseado
            porcentaje_recorte = 0.10
            margen_recorte_ancho = int(target_size[0] * porcentaje_recorte)
            margen_recorte_alto = int(target_size[1] * porcentaje_recorte)
            # Definir las coordenadas de recorte
            x1 = margen_recorte_ancho
            y1 = margen_recorte_alto
            x2 = target_size[0] - margen_recorte_ancho
            y2 = target_size[1] - margen_recorte_alto
            # Recortar la región de interés dentro de los márgenes recortados
            roi = resized_frame[y1:y2, x1:x2]
            # Procesar el frame recortado
            process_frame(roi)
            frame_count += 1
            # Verificar si han pasado 10 segundos sin recibir tramas
            current_time = time.time()
            elapsed_time = current_time - last_frame_time
            if elapsed_time > 6:
                print("Han pasado 10 segundos sin recibir tramas. Solicitando nueva transmisión...")
                break  # Romper el bucle y solicitar una nueva transmisión
            last_frame_time = current_time
    except cv2.error as e:
        logger.error(f"Error al abrir el video: {e}")
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


alpr = ALPR()
configure = get_model_config()
#video_path = '/home/pepe/Descargas/test_l4.mp4'
video_path = RTSPClient().get_connection()

logger.critical(f'Se va analizar la fuente: {video_path}')
intervalo_reconocimiento = configure.frecuencia_inferencia
if not cv2.haveImageReader(video_path):
    logger.critical(f'El intervalo del reconocimiento para el video es de: {intervalo_reconocimiento}')

capture_thread = threading.Thread(target=capture_frames)
capture_thread.start()

client.on_connect = on_connect
if username and password:
    client.username_pw_set(username, password)
client.connect(broker, port)
client.loop_start()

capture_thread.join()

client.loop_stop()
client.disconnect()

import time
import jaro
from datetime import datetime
import threading
import cv2
import os
import paho.mqtt.client as mqtt
import logging

from config.config import get_model_config, get_directory_config, get_database_url, get_mqtt_config
from database.database import get_session, init_sin_tunel_database
from database.empresas import Empresas
from database.transporte_egreso import TransporteEgreso
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
    client.publish(topico_barrera, "#out1-pulse")
    client.publish(topico_camara, "#image-simple")
    time.sleep(1)
    client.publish(topico_camara, "#image-simple")
    time.sleep(1)
    client.publish(topico_camara, "#image-simple")
    time.sleep(1)
    client.publish(topico_camara, "#video-simple")
    client.publish(topico_semaforo, "#out1-off")


def zoom_image(image, scale_factor):
    return cv2.resize(image, None, fx=scale_factor, fy=scale_factor)


def recortar_patente(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]


def process_frame(frame):
    directory_storage = get_directory_config()
    predicts = list(alpr.show_predicts(frame))
    if not predicts:
        return

    habilitado = 1
    resultados = session.query(TransporteVehiculos).filter(TransporteVehiculos.habilitado == habilitado).all()
    session.commit()
    aproximado = {
        'id': '',
        'patente': '',
        'distancia_jaro': -1
    }
    for predict in predicts:
        distancias_jaro = [jaro.jaro_winkler_metric(resultado.patente, predict.patente) for resultado in resultados]
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
        print('Patente no habilitada', predict.patente)
    else:
        transport_vehiculos = session.query(TransporteVehiculos).filter(
            TransporteVehiculos.id == aproximado['id']).first()
        if transport_vehiculos:
            empresa = session.query(Empresas).filter(Empresas.id == transport_vehiculos.empresaId).first()
            egreso_veiculo = TransporteEgreso(
                empresa_id=empresa.id,
                empresa=empresa.razonSocial,
                patente=aproximado['patente'],
                procesado=True,
                fecha_salida=datetime.now().date(),
                hora_salida=datetime.now().time(),
                lectura_forzada=False,
                motivo=''
            )
            session.add(egreso_veiculo)
            session.commit()
            print('se inserta: ', aproximado['patente'])
            transporte = session.query(TransporteVehiculos).filter(
                TransporteVehiculos.patente == aproximado['patente']).first()
            transporte.habilitado = False
            session.commit()
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
            imagen_path = os.path.join(directory_storage.destination, f'{timestamp}_patente.jpg')
            x1, y1, x2, y2 = predicts[0].posicion
            plate_region = recortar_patente(frame, x1, y1, x2, y2)
            zoomed_plate_region = zoom_image(plate_region, scale_factor=2.5)
            cv2.imwrite(imagen_path, zoomed_plate_region)
            imagen_path = os.path.join(directory_storage.destination, f'{timestamp}.jpg')
            cv2.imwrite(imagen_path, frame)


def capture_frames():
    cap = cv2.VideoCapture(video_path)
    try:
        while cap.isOpened():
            return_value, frame = cap.read()
            if not return_value:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            process_frame(frame)
    finally:
        cap.release()


alpr = ALPR()
configure = get_model_config()
video_path = '/home/pepe/Descargas/testl.mp4'
# video_path = RTSPClient().get_connection()

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

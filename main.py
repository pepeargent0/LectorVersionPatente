import time
from time import sleep
import jaro
from datetime import datetime

from camara.rtsp import RTSPClient
from config.config import get_model_config, get_directory_config, get_database_url, get_mqtt_config
from database.database import get_session, init_sin_tunel_database
from database.empresas import Empresas
from database.transporte_egreso import TransporteEgreso
from database.transporte_vehiculos import TransporteVehiculos
from patentes.alpr import ALPR
import paho.mqtt.client as mqtt
import logging
import cv2
import  os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


def on_connect(client, userdata, flags, rc):
    client.publish(topico_semaforo, "#out1-off")
    client.publish(topico_semaforo, "#out2-on")
    client.publish(topico_barrera, "#out1-pulse")
    client.publish(topico_camara, "#image-simple")
    sleep(1)
    client.publish(topico_camara, "#image-simple")
    sleep(1)
    client.publish(topico_camara, "#image-simple")
    sleep(1)
    client.publish(topico_camara, "#video-simple")
    client.publish(topico_semaforo, "#out1-off")


def zoom_image(image, scale_factor):
    height, width = image.shape[:2]
    new_height = int(height * scale_factor)
    new_width = int(width * scale_factor)
    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image


alpr = ALPR()
configure = get_model_config()
#video_path = '/home/pepe/Descargas/testl.mp4'
video_path = RTSPClient().get_connection()

cap = cv2.VideoCapture(video_path)
is_img = cv2.haveImageReader(video_path)
logger.info(f'Se va analizar la fuente: {video_path}')
frame_id = 0
intervalo_reconocimiento = configure.frecuencia_inferencia
if not is_img:
    logger.info(f'El intervalo del reconocimiento para el video es de: {intervalo_reconocimiento}')


def recortar_patente(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]


while True:
    return_value, frame = cap.read()
    if return_value:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        # Descomenten esto para camara IP Esto es por si el stream deja de transmitir algún
        # frame o se tarda más de lo normal. En este caso simplemente volvemos a intentar leer el frame.
        vid = cv2.VideoCapture(video_path)
        continue
        #break
    directory_storage = get_directory_config()
    for predict in alpr.show_predicts(frame):
        # predict.patente = 'dss164'cc
        print('prediccion: ', predict.patente)
        habilitado = 1
        aproximado = {
            'id': '',
            'patente': '',
            'distancia_jaro': -1
        }
        patente = True
        resultados = session.query(TransporteVehiculos).filter(TransporteVehiculos.habilitado == habilitado).all()
        for resultado in resultados:
            distancia_jaro = jaro.jaro_winkler_metric(resultado.patente, predict.patente)
            if not aproximado or aproximado['distancia_jaro'] < distancia_jaro:
                aproximado = {
                    'id': resultado.id,
                    'patente': resultado.patente,
                    'distancia_jaro': distancia_jaro
                }
        if aproximado['distancia_jaro'] < 0.70:
            print('patente no habilitada', predict.patente)
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
                if patente:
                    imagen_path = directory_storage.destination + '/' + timestamp + '_patente.jpg'
                    x1, y1, x2, y2 = predict.posicion
                    plate_region = recortar_patente(frame, x1, y1, x2, y2)
                    zoomed_plate_region = zoom_image(
                        plate_region,
                        scale_factor=2.5
                    )
                    cv2.imwrite(imagen_path, zoomed_plate_region)
                    patente = False
                imagen_path = directory_storage.destination + '/' + timestamp + '.jpg'
                cv2.imwrite(imagen_path, frame)
                time.sleep(10)
                # MQTT
                client = mqtt.Client()
                if not username and not password:
                    client.username_pw_set(username, password)
                client.on_connect = on_connect
                client.connect(broker, port)
                client.loop_start()
                sleep(4)
                client.loop_stop()
                client.disconnect()
                break
    frame_id += 1
cap.release()
cv2.destroyAllWindows()

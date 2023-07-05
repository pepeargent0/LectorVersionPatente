# Ruta de la URL RTSPrtsp_url = "rtsp://admin:Admin123@oficina.lagasystems.com.ar:554"  # Actualiza con tu URL RTSP
import time

from patentes.alpr import ALPR
import yaml
import logging
import cv2

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main_demo(cfg):
    alpr = ALPR()
    # video_path = "rtsp://admin:Admin123@oficina.lagasystems.com.ar:554"

    video_path = '/home/pepe/Descargas/test12.mp4'
    cap = cv2.VideoCapture(video_path)
    is_img = cv2.haveImageReader(video_path)
    logger.info(f'Se va analizar la fuente: {video_path}')
    frame_id = 0
    # Cada cuantos frames hacer inferencia
    intervalo_reconocimiento = cfg['video']['frecuencia_inferencia']
    if not is_img:
        logger.info(f'El intervalo del reconocimiento para el video es de: {intervalo_reconocimiento}')
    while True:
        return_value, frame = cap.read()
        if return_value:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            # Descomenten esto para camara IP Esto es por si el stream deja de transmitir algún
            # frame o se tarda más de lo normal. En este caso simplemente volvemos a intentar leer el frame.
            # vid = cv2.VideoCapture(video_path)
            # continue
            break
        inicio = time.time()
        for predict in alpr.show_predicts(frame):
            print('precicion: ', predict, 'tiempo: ', time.time() - inicio)

        """
        mostramos video  demo:
            frame_w_pred, total_time = alpr.mostrar_predicts(
                frame)
            frame_w_pred = cv2.cvtColor(frame_w_pred, cv2.COLOR_RGB2BGR)
            frame_w_pred_r = cv2.resize(frame_w_pred, dsize=(1400, 1000))
            cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("result %", frame_w_pred_r)

            if cv2.waitKey(cv2_wait) & 0xFF == ord('q'):
                break
        """
        frame_id += 1
    cap.release()
    cv2.destroyAllWindows()


try:
    with open('config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
except yaml.YAMLError as exc:
    logger.exception(exc)
main_demo(cfg)

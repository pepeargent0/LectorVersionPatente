import os
from timeit import default_timer as timer
from dotenv import load_dotenv

import cv2
import numpy as np
from pydantic import BaseModel

from config.config import get_model_config
from .detector import PlateDetector
from .ocr import PlateOCR


class Predict(BaseModel):
    patente: str
    porcentaje: float
    posicion: tuple


class ALPR:
    def __init__(self):
        configure = get_model_config()
        input_size = configure.resolution_detector
        if input_size not in (384, 512, 608):
            raise ValueError('Modelo detector no existe! Opciones { 384, 512, 608 }')
        detector_path = f'patentes/models/detection/tf-yolo_tiny_v4-{input_size}x{input_size}-custom-anchors/'
        self.detector = PlateDetector(
            detector_path,
            input_size,
            score=configure.resolution_confianza
        )
        self.ocr = PlateOCR(
            configure.number_model,
            configure.avg_ocr,
            configure.confianza_low_ocr
        )
        self.processed_predictions = {}  # Diccionario para almacenar las predicciones procesadas

    def predict(self, frame: np.ndarray) -> list:
        input_img = self.detector.preprocess(frame)
        yolo_out = self.detector.predict(input_img)
        bboxes = self.detector.procesar_salida_yolo(yolo_out)
        iter_coords = self.detector.yield_coords(frame, bboxes)
        patentes = self.ocr.predict(iter_coords, frame)
        return patentes

    def show_predicts(self, frame: np.ndarray):
        input_img = self.detector.preprocess(frame)
        # print(input_img)
        yolo_out = self.detector.predict(input_img)
        bboxes = self.detector.procesar_salida_yolo(yolo_out)
        iter_coords = self.detector.yield_coords(frame, bboxes)

        # print(iter_coords)
        for x1, y1, x2, y2, _ in iter_coords:
            #print(x1, y1, x2, y2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (36, 255, 12), 2)
            #print(x1, y1, x2, y2, frame)
            plate, probs = self.ocr.predict_ocr(x1, y1, x2, y2, frame)
            avg = np.mean(probs)
            load_dotenv()
            if avg > self.ocr.confianza_avg:
                plate = ''.join(plate).replace('_', '')
                return Predict(patente=plate, porcentaje=avg * 100, posicion=(x1, y1, x2, y2))


    def mostrar_predicts(self, frame: np.ndarray):
        total_time = 0
        start = timer()
        input_img = self.detector.preprocess(frame)
        yolo_out = self.detector.predict(input_img)
        bboxes = self.detector.procesar_salida_yolo(yolo_out)
        iter_coords = self.detector.yield_coords(frame, bboxes)
        end = timer()
        total_time += end - start
        font_scale = 1.25
        for x1, y1, x2, y2, _ in iter_coords:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (36, 255, 12), 2)
            start = timer()
            plate, probs = self.ocr.predict_ocr(x1, y1, x2, y2, frame)
            total_time += timer() - start
            avg = np.mean(probs)
            if avg > self.ocr.confianza_avg and self.ocr.none_low(probs, thresh=self.ocr.none_low_thresh):
                plate = ''.join(plate).replace('_', '')
                current_time = timer()
                if plate not in self.processed_predictions or current_time - self.processed_predictions[plate] > 3600:
                    self.processed_predictions[plate] = current_time
                    mostrar_txt = f'{plate} {avg * 100:.2f}%'
                    cv2.putText(
                        img=frame,
                        text=mostrar_txt,
                        org=(x1 - 20, y1 - 15),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=font_scale,
                        color=[0, 0, 0],
                        lineType=cv2.LINE_AA,
                        thickness=6
                    )
                    cv2.putText(
                        img=frame,
                        text=mostrar_txt,
                        org=(x1 - 20, y1 - 15),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=font_scale,
                        color=[255, 255, 255],
                        lineType=cv2.LINE_AA,
                        thickness=2
                    )
        return frame, total_time

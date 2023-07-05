from dotenv import load_dotenv
from pydantic import BaseModel
import pymysql
import os


class Directory(BaseModel):
    destination: str


class ModelConfig(BaseModel):
    resolution_detector: int
    resolution_confianza: float
    avg_ocr: float
    number_model: int
    confianza_low_ocr: float
    frecuencia_inferencia: int


class RtspConfig(BaseModel):
    """
    Configuración para la conexión RTSP.

    Attributes:
        host (str): Host del servidor RTSP.
        port (int): port
        username (str): Nombre de usuario para la autenticación.
        password (str): Contraseña para la autenticación.
    """
    host: str
    port: int
    username: str
    password: str


class DataBaseConnection(BaseModel):
    """
    Configuración para la conexión a la base de datos.

    Attributes:
        server (str): Dirección del servidor de la base de datos.
        port (int): Puerto del servidor de la base de datos.
        username (str): Nombre de usuario para la autenticación.
        password (str): Contraseña para la autenticación.
    """
    server: str
    port: int
    username: str
    password: str
    database: str


class MqttConnection(BaseModel):
    """
    Configuración para la conexión MQTT.

    Attributes:
        broker (str): Dirección del broker MQTT.
        port (int): Puerto del broker MQTT.
        username (str): Nombre de usuario para la autenticación.
        password (str): Contraseña para la autenticación.
        camara (str): topic camara
        barrera (str): topic barrera
        semaforo (str): topic semaforo
    """
    broker: str
    port: int
    username: str
    password: str
    camara: str
    barrera: str
    semaforo: str


def get_directory_config() -> Directory:
    load_dotenv()
    destination = os.getenv('DIRECTORY')
    if not destination:
        error_msg = "Faltan las siguientes variables de entorno: DIRECTORY"
        raise EnvironmentError(error_msg)
    directory = Directory(
        destination=destination
    )
    return directory


def get_model_config() -> ModelConfig:
    load_dotenv()
    resolution_detector = os.getenv('RESOLUCION_DETECTOR')
    resolution_confianza = os.getenv('RESOLUCION_CONFIANZA')
    avg_ocr = os.getenv('AVG_OCR')
    number_model = os.getenv('NRO_MODELO')
    confianza_low_ocr = os.getenv('CONFIANZA_LOW_OCR')
    frecuencia_inferencia = os.getenv('FRECUENCIA_INFERENCIA')
    missing_vars = []
    if not resolution_detector:
        missing_vars.append('RESOLUCION_DETECTOR')
    if not resolution_confianza:
        missing_vars.append('RESOLUCION_CONFIANZA')
    if not avg_ocr:
        missing_vars.append('AVG_OCR')
    if not number_model:
        missing_vars.append('NRO_MODELO')
    if not confianza_low_ocr:
        missing_vars.append('CONFIANZA_LOW_OCR')
    if not frecuencia_inferencia:
        missing_vars.append('FRECUENCIA_INFERENCIA')

    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        error_msg = f"Faltan las siguientes variables de entorno: {missing_vars_str}"
        raise EnvironmentError(error_msg)

    config_model = ModelConfig(
        resolution_detector=resolution_detector,
        resolution_confianza=resolution_confianza,
        avg_ocr=avg_ocr,
        number_model=number_model,
        confianza_low_ocr=confianza_low_ocr,
        frecuencia_inferencia=frecuencia_inferencia
    )
    return config_model


def get_mqtt_config() -> MqttConnection:
    """
    Obtiene la configuración para la conexión MQTT desde las variables de entorno.

    Returns:
        MqttConnection: Objeto que contiene la configuración MQTT.

    Raises:
        EnvironmentError: Si alguna variable de entorno está ausente.
    """
    load_dotenv()

    broker = os.getenv('MQTT_BROKER')
    port = os.getenv('MQTT_PORT')
    username = os.getenv('MQTT_USER')
    password = os.getenv('MQTT_PASSWORD')
    camara = os.getenv('TOPIC_CAMARA')
    barrera = os.getenv('TOPIC_BARRERA')
    semaforo = os.getenv('TOPIC_SEMAFORO')
    missing_vars = []
    if not broker:
        missing_vars.append('MQTT_BROKER')
    if not port:
        missing_vars.append('MQTT_PORT')
    if not username:
        missing_vars.append('MQTT_USER')
    if not password:
        missing_vars.append('MQTT_PASSWORD')
    if not camara:
        missing_vars.append('TOPIC_CAMARA')
    if not barrera:
        missing_vars.append('TOPIC_BARRERA')
    if not semaforo:
        missing_vars.append('TOPIC_SEMAFORO')

    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        error_msg = f"Faltan las siguientes variables de entorno: {missing_vars_str}"
        raise EnvironmentError(error_msg)

    connection_mqtt = MqttConnection(
        broker=broker,
        port=port,
        username=username,
        password=password,
        camara=camara,
        barrera=barrera,
        semaforo=semaforo
    )
    return connection_mqtt


def get_rtsp_config() -> RtspConfig:
    """
    Obtiene la configuración para la conexión RTSP desde las variables de entorno.

    Returns:
        RtspConfig: Objeto que contiene la configuración RTSP.

    Raises:
        EnvironmentError: Si alguna variable de entorno está ausente.
    """
    load_dotenv()
    host = os.getenv('RTSP_HOST')
    port = os.getenv('RTSP_PORT')
    username = os.getenv('RTSP_USER')
    password = os.getenv('RTSP_PASSWORD')

    missing_vars = []
    if not host:
        missing_vars.append('RTSP_HOST')
    if not port:
        missing_vars.append('RTSP_PORT')
    if not username:
        missing_vars.append('RTSP_USER')
    if not password:
        missing_vars.append('RTSP_PASSWORD')

    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        error_msg = f"Faltan las siguientes variables de entorno: {missing_vars_str}"
        raise EnvironmentError(error_msg)

    connection_rtsp = RtspConfig(
        host=host,
        port=port,
        username=username,
        password=password
    )
    return connection_rtsp


def get_database_config() -> DataBaseConnection:
    """
    Obtiene la configuración para la conexión a la base de datos desde las variables de entorno.

    Returns:
        DataBaseConnection: Objeto que contiene la configuración de la base de datos.

    Raises:
        EnvironmentError: Si alguna variable de entorno está ausente.
    """
    load_dotenv()
    server = os.getenv('DB_SERVER')
    port = os.getenv('DB_PORT')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    missing_vars = []
    if not database:
        missing_vars.append('DB_NAME')
    if not server:
        missing_vars.append('DB_SERVER')
    if not port:
        missing_vars.append('DB_PORT')
    if not username:
        missing_vars.append('DB_USER')
    if not password:
        missing_vars.append('DB_PASSWORD')
    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        error_msg = f"Faltan las siguientes variables de entorno: {missing_vars_str}"
        raise EnvironmentError(error_msg)

    database_connection = DataBaseConnection(
        server=server,
        port=port,
        username=username,
        password=password,
        database=database
    )
    return database_connection


def get_database_url():
    coneccion_db = get_database_config()
    return f"mysql+pymysql://{coneccion_db.username}:" \
           f"{coneccion_db.password}@{coneccion_db.server}/{coneccion_db.database}"


class SSHConfig(BaseModel):
    host: str
    port: int
    username: str
    password: str


def get_config_ssh():
    load_dotenv()
    host = os.getenv('SSH_HOST')
    port = os.getenv('SSH_PORT')
    username = os.getenv('SSH_USER')
    password = os.getenv('SSH_PASSWORD')
    missing_vars = []
    if not host:
        missing_vars.append('SSH_HOST')
    if not port:
        missing_vars.append('SSH_PORT')
    if not username:
        missing_vars.append('SSH_USER')
    if not password:
        missing_vars.append('SSH_PASSWORD')
    if missing_vars:
        missing_vars_str = ', '.join(missing_vars)
        error_msg = f"Faltan las siguientes variables de entorno: {missing_vars_str}"
        raise EnvironmentError(error_msg)
    conection_ssh = SSHConfig(
        host=host,
        port=port,
        password=password,
        username=username
    )
    return conection_ssh


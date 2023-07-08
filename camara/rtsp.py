from config.config import get_rtsp_config


class RTSPClient:
    """
    Clase para manejar un cliente RTSP.
    """

    def __init__(self):
        """
        Inicializa una instancia de RTSPClient.
        """
        config = get_rtsp_config()
        self.host = config.host
        self.port = config.port
        self.username = config.username
        self.password = config.password

    def get_connection(self):
        """
        Conecta al servidor RTSP y comienza la reproducción.
        """
        connection = 'rtsp://'
        if self.username != '' and self.password != '':
            connection += self.username + ':' + self.password + '@'
        connection += self.host + ':' + str(self.port)+'?tcp'
        return connection

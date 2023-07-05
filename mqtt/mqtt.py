import paho.mqtt.client as mqtt


class MqttSender:
    """
    Clase para enviar mensajes MQTT utilizando la biblioteca paho-mqtt.

    Attributes:
        broker (str): Dirección del broker MQTT.
        port (int): Puerto del broker MQTT.
        username (str, optional): Nombre de usuario para la autenticación en el broker MQTT.
        password (str, optional): Contraseña para la autenticación en el broker MQTT.
    """

    def __init__(self, broker, port, username=None, password=None):
        """
        Inicializa una instancia de la clase MqttSender.

        Args:
            broker (str): Dirección del broker MQTT.
            port (int): Puerto del broker MQTT.
            username (str, optional): Nombre de usuario para la autenticación en el broker MQTT.
            password (str, optional): Contraseña para la autenticación en el broker MQTT.
        """
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client = mqtt.Client()

        if username and password:
            self.client.username_pw_set(username, password)

    def connect(self):
        """
        Establece la conexión con el broker MQTT.
        """
        self.client.connect(self.broker, self.port)

    def send_message(self, topic, message):
        """
        Envía un mensaje MQTT a un tema específico.

        Args:
            topic (str): Tema al que se enviará el mensaje.
            message (str): Mensaje a enviar.
        """
        self.client.publish(topic, message)

    def disconnect(self):
        """
        Cierra la conexión con el broker MQTT.
        """
        self.client.disconnect()

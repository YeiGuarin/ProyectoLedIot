import time
import json
import uuid
import paho.mqtt.client as mqtt
from encriptacion import decrypt, ENCRYPTION_PASSWORD, aes_encrypt, encrypt
from binascii_converter import convert_to_hex, convert_to_bytes, convert_from_hex, is_valid_hex

# -----------------------------------------------------------------------------
# Configuración Global
# -----------------------------------------------------------------------------

TOPICO_MQTT = "esp32/Yeimy"  # Tópico MQTT al que el cliente se suscribe y publica


# -----------------------------------------------------------------------------
# Creación y Configuración del Cliente MQTT
# -----------------------------------------------------------------------------

def crear_cliente():
    """
    Crea y retorna un cliente MQTT sin conectarlo todavía.

    Returns:
        mqtt.Client: Instancia del cliente MQTT.
    """
    return mqtt.Client()


def asignar_mac(cliente):
    """
    Asigna una identificación única (MAC simulada) al cliente MQTT usando UUID.

    Args:
        cliente (mqtt.Client): Cliente MQTT.

    Returns:
        str: Identificador en formato hexadecimal.
    """
    unique_id = uuid.uuid4()  # Generar UUID único
    mac = convert_to_hex(unique_id.bytes)  # Convertir a hex
    cliente._client_id = mac.encode()  # Asignar como ID del cliente
    return mac


def conectar_mqtt(cliente, tipo_cliente):
    """
    Establece la conexión del cliente al broker MQTT.

    Args:
        cliente (mqtt.Client): Cliente MQTT.
        tipo_cliente (str): Descripción del cliente (usado para logs).
    """
    try:
        HOST = "mqtt.eclipseprojects.io"
        port = 1883
        cliente.connect(HOST, port)
        print(f"Conexión exitosa al broker MQTT desde {cliente._client_id} como {tipo_cliente}")
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
        cliente.reconnect()


# -----------------------------------------------------------------------------
# Callbacks de Cliente MQTT
# -----------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    """
    Callback ejecutado al establecer conexión con el broker.

    Args:
        client: Cliente MQTT.
        userdata: Datos adicionales (no utilizados).
        flags: Flags de conexión.
        rc (int): Código de resultado (0 = OK).
    """
    print(f"Conectado al broker MQTT con código {rc}")
    if rc == 0:
        client.subscribe(TOPICO_MQTT)
        print(f"Suscripción exitosa al tópico: {TOPICO_MQTT}")
    else:
        print(f"Error en la conexión. Código de retorno: {rc}")


def on_disconnect(client, userdata, rc):
    """
    Callback ejecutado al desconectarse del broker MQTT.

    Args:
        client: Cliente MQTT.
        userdata: Datos adicionales (no utilizados).
        rc (int): Código de desconexión.
    """
    print(f"Desconectado del broker MQTT con código: {rc}")
    if rc != 0:
        print("Intentando reconectar...")
        for intento in range(5):  # Reintentos exponenciales
            try:
                client.reconnect()
                print("Reconexión exitosa.")
                return
            except Exception as e:
                print(f"Error al intentar reconectar: {e}")
                time.sleep(2 ** intento)


def on_message(client, userdata, msg):
    """
    Callback ejecutado al recibir un mensaje desde el tópico suscrito.

    Args:
        client: Cliente MQTT.
        userdata: Datos adicionales.
        msg (MQTTMessage): Mensaje recibido.
    """
    try:
        message = msg.payload.decode()
        print(f"Mensaje recibido en {msg.topic}: {message}")

        # Verificar que el mensaje esté en hexadecimal
        if not is_valid_hex(message):
            print("El mensaje recibido no está en formato hexadecimal.")
            return

        # Convertir a bytes y descifrar
        encrypted_data = convert_to_bytes(message)

        try:
            decrypted_message = decrypt(encrypted_data, ENCRYPTION_PASSWORD)
            print(f"Mensaje descifrado: {decrypted_message}")

            # Procesar JSON
            try:
                processed_data = json.loads(decrypted_message)
                print(f"Mensaje procesado: {processed_data}")
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
        except Exception as e:
            print(f"Error al descifrar mensaje: {e}")
    except Exception as e:
        print(f"Error en on_message: {e}")


# -----------------------------------------------------------------------------
# Publicación de Mensajes
# -----------------------------------------------------------------------------

def publicar_estado(cliente, estado):
    """
    Publica un mensaje cifrado al tópico MQTT.

    Args:
        cliente (mqtt.Client): Cliente MQTT.
        estado (dict): Datos a publicar.
    """
    try:
        mensaje = json.dumps(estado)  # Convertir a JSON
        datos_cifrados = encrypt(mensaje, ENCRYPTION_PASSWORD)
        estado_hex = convert_to_hex(datos_cifrados)

        result = cliente.publish(TOPICO_MQTT, estado_hex)
        result.wait_for_publish()
        print(f"Estado publicado: {estado_hex}")
    except Exception as e:
        print(f"Error al publicar estado en MQTT: {e}")

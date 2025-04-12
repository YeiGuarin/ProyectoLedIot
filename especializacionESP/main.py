import hashlib
import os
import time
import umqtt.robust
import socket
from time import sleep
import ujson
import _thread
import ubinascii
from machine import Pin
import network
import machine
import gc
from ubinascii import hexlify, unhexlify
from gestionConexion import buscarRed
import uos
import hashlib
from ucryptolib import aes

# Contraseña para encriptación
ENCRYPTION_PASSWORD = "especializacion"
MODE_CBC = 2

# Funciones para encriptación y desencriptación en MicroPython
def generate_key(password):
    """Genera una clave AES de 16 bytes a partir de una contraseña."""
    return hashlib.sha256(b'0123456789ABCDEF').digest()

def generate_iv():
    """Genera un IV estático (fijo) de 16 bytes."""
    #return b'\0' * 16
    return b'0123456789ABCDEF'

def pad(data):
    """Aplica padding PKCS#7 a los datos."""
    return data + " " * (16 - len(data) % 16)

def unpad(data):
    """Elimina el padding PKCS#7 de los datos."""
    padding_len = data[-1]  # El último byte indica el número de bytes de padding
    if padding_len < 1 or padding_len > 16:  # Validar que el padding sea correcto
        raise ValueError("Padding inválido.")
    return data[:-padding_len]


def encrypt(data, password):
    """Cifra datos utilizando AES en modo CBC."""
    key = generate_key(password)
    iv = generate_iv()  # IV dinámico
    cipher = aes(key, MODE_CBC, iv)
    padded_data = pad(data)
    encrypted_data = cipher.encrypt(padded_data)
    print('encriptado desde esp 32: {}'.format(encrypted_data))
    return encrypted_data  # Concatenar IV y datos cifrados

def decrypt(encrypted_data, password):
    """Descifra datos utilizando AES en modo CBC."""
    key = generate_key(password)
    iv = generate_iv()  # Extraer IV de los primeros 16 bytes
    decipher = aes(key, MODE_CBC, iv)
    decrypted = decipher.decrypt(encrypted_data)
    return unpad(decrypted)

# Configuración de red
time.sleep(5)
archivoRed = open("red", "r")
informacion = ujson.loads(archivoRed.read())
archivoRed.close()
estadoRed = buscarRed(informacion['ssid'], informacion['contrasena'])
if not estadoRed:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="ESPYEIMY", password="123456789", authmode=2)
    print(ap.ifconfig())

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 80))
    server_socket.listen(5)
    print('Esperando conexiones...')

# Configuración de MQTT y pines
sleep(1)
host = "mqtt.eclipseprojects.io"
mac = ubinascii.hexlify(machine.unique_id())

clientMQTT = umqtt.robust.MQTTClient(mac, host)

# Tópicos para publicar y suscribirse
topico_publicar = "esp32/Yeimy"

topico_suscribir = "esp32/Yeimy"

# Configurar LED y botón
boton = Pin(14, Pin.IN, Pin.PULL_UP)
Led = Pin(27, Pin.OUT)
estadoAnterior = boton.value()

# Estado anterior publicado para evitar publicaciones redundantes
estadoAnteriorPublicado = None


# Callback para mensajes MQTT
def sub_cb(topic, msg):
    print(f'Recibido en esp en {topic}: {msg}')
    try:
        if isinstance(msg, bytes):
            # Intentar descifrar el mensaje
            print(f'Desencriptando desde esp 32: {msg}')
            encrypted_data = unhexlify(msg)  # Convertir de hexadecimal a bytes
            decrypted_message = decrypt(encrypted_data, ENCRYPTION_PASSWORD)
        else:
            decrypted_message = msg  # Tratarlo como texto plano
        print(f'Desencriptado desde esp 32: {decrypted_message.strip()}')

        # Intentar cargar como JSON
        datoEntrada = ujson.loads(decrypted_message)
        print(f'Dato de entrada JSON: {datoEntrada}')

        if 'estadoPin' in datoEntrada:
            if datoEntrada['estadoPin'] == 0:
                Led.on()
                print(f"LED Encendido desde {topic.decode()}")
            elif datoEntrada['estadoPin'] == 1:
                Led.off()
                print(f"LED Apagado desde {topic.decode()}")
    except ValueError as ve:
        print(f"Error al procesar el mensaje MQTT (formato inválido): {ve}")
    except Exception as e:
        print(f"Error al procesar el mensaje MQTT: {e}")
    finally:
        gc.collect()



# Configuración de MQTT
clientMQTT.set_callback(sub_cb)
clientMQTT.connect()

# Suscribirse al tópico
clientMQTT.subscribe(topico_suscribir)
print(f'Suscrito a {topico_suscribir}')


# Hilo para escuchar mensajes MQTT
def funcion_suscribirse():
    while True:
        try:
            clientMQTT.check_msg()
        except Exception as e:
            print(f"Error al recibir mensajes: {e}")


_thread.start_new_thread(funcion_suscribirse, ())


# Publicar estado en MQTT con encriptación
def publicar_estado(estado):
    global estadoAnteriorPublicado
    if estado != estadoAnteriorPublicado:
        estadoAnteriorPublicado = estado
        estado_str = ujson.dumps({"estadoPin": estado})
        encrypted_state = encrypt(estado_str, ENCRYPTION_PASSWORD)
        print('encriptado desde esp 32: {}'.format(encrypted_state))
        clientMQTT.publish(topico_publicar, hexlify(encrypted_state))
        print(f'Publicado en {topico_publicar}: {hexlify(encrypted_state).decode()}')
        gc.collect()  # Liberar memoria después de cada acción


# Controlar el LED con el botón físico
def controlar_led_con_boton():
    global estadoAnterior
    while True:
        nuevoEstado = boton.value()
        if nuevoEstado != estadoAnterior:
            estadoAnterior = nuevoEstado
            if nuevoEstado == 0:
                Led.on()
                publicar_estado(0)
                #telegram_bot.enviar_mensaje_telegram("LED encendido localmente por el botón")
            else:
                Led.off()
                publicar_estado(1)
                #telegram_bot.enviar_mensaje_telegram("LED apagado localmente por el botón")
            gc.collect()  # Liberar memoria después de cada acción
        sleep(0.1)


_thread.start_new_thread(controlar_led_con_boton, ())
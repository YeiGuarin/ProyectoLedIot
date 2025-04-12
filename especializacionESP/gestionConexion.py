import network
import time
from machine import Pin

def buscarRed(nombreRed = "nombreRed", contrasena="contraseñaRed"):

    led = Pin(2, Pin.OUT)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(nombreRed,contrasena)
    estadoWifi = False
    contador = 0
    while not wifi.isconnected():
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(1)
        if contador > 50:
            break
        contador += 1

# Imprimir el estado de la conexion usando wifi.status

    if wifi.isconnected():
        led.on()
        print("Conectado a la red, Configuracion IP", wifi.ifconfig())
        estadoWifi = True
    else:
        print("No se pudo conectar a la red")
    return estadoWifi

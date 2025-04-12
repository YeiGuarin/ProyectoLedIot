# Proyecto de Control de LED y Gestión de Usuarios con MicroPython y Telegram

Este proyecto tiene como objetivo controlar un LED conectado a un ESP32 y gestionar usuarios a través de un bot de Telegram, con soporte para cifrado de comunicaciones y autenticación de usuarios. El sistema también utiliza MQTT para la comunicación entre el ESP32 y otros dispositivos.

## Requisitos

El proyecto utiliza un entorno de desarrollo Conda para gestionar las dependencias en Python, así como las librerías necesarias para trabajar con MicroPython en el ESP32.

### Requisitos para el entorno Conda (PC)

1. **Instalar Conda**:
   - Si no tienes Conda instalado, puedes instalar [Anaconda](https://www.anaconda.com/products/distribution) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
   
2. **Crear un entorno virtual**:
   - Crea un entorno Conda para el proyecto:
     ```bash
     conda create -n esp32_project python=3.x
     ```
   - Activa el entorno virtual:
     ```bash
     conda activate esp32_project
     ```

3. **Instalar las dependencias**:
   - Instalar las librerías necesarias:
     ```bash
     pip install paho-mqtt cryptography psycopg2 umqtt.simple
     ```

### Requisitos para MicroPython (ESP32)

1. **Instalar MicroPython en el ESP32**:
   - Flashear el firmware de MicroPython en el ESP32. Puedes encontrar las instrucciones [aquí](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).

2. **Librerías necesarias para MicroPython**:
   - Para manejar la comunicación MQTT y el cifrado AES, se utilizan las siguientes librerías:
     - `umqtt.simple` para MQTT.
     - `ucryptolib` para el cifrado AES.
     - `ujson` para manejar datos JSON.
   - Puedes instalar estas librerías en MicroPython a través del gestor de paquetes `upip`.

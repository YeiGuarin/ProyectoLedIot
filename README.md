# Proyecto ESP32 + Telegram Bot: Control de LED y Gestión de Usuarios

Este proyecto permite controlar un LED conectado a un ESP32 a través de un botón físico o un bot de Telegram. También implementa autenticación de usuarios mediante una base de datos PostgreSQL y asegura la comunicación con cifrado AES sobre MQTT.

Se divide en dos partes principales:
- **MicroPython en ESP32**: Maneja la conexión Wi-Fi, control del LED, comunicación MQTT y cifrado AES.
- **Bot de Telegram en PC**: Gestiona usuarios, permite enviar comandos al ESP32 y almacena logs en la base de datos.

## Archivos principales

- 🔌 [`Micropython`](./especializacionESP/readme.md): Código principal que corre en el ESP32, gestiona la conexión a Wi-Fi, MQTT, cifrado y el control del LED.
- 🤖 [`bot_telegram.py`](./especializacionIoT/readme.md): Bot de Telegram que interactúa con usuarios, recibe comandos y los publica cifrados al ESP32.

## Descripción general del flujo

1. El ESP32 se conecta a una red Wi-Fi (almacenada en un archivo).
2. Se suscribe a un tópico MQTT y espera comandos cifrados.
3. El bot de Telegram permite a los usuarios registrados encender/apagar el LED.
4. Las acciones quedan registradas en una base de datos PostgreSQL.
5. Todo el sistema está protegido con cifrado AES-256 en modo CBC para asegurar los mensajes.

> 🛠 El entorno de desarrollo usa **Conda** y librerías como `paho-mqtt`, `cryptography`, `psycopg2` en la PC, y `umqtt.simple`, `ucryptolib`, `ujson` en MicroPython para el ESP32.

---

¡Este proyecto es ideal para aprender sobre IoT, cifrado, bots y automatización en redes seguras!

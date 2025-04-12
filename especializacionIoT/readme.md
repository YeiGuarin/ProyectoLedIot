## Descripción del Proyecto

### 1. **Control de LED con el ESP32**
   - El ESP32 se conecta a una red Wi-Fi configurada previamente (almacenada en un archivo JSON).
   - Si no puede conectarse, se crea un punto de acceso (AP) para facilitar la configuración.
   - El estado del LED se controla a través de un botón físico o mediante comandos MQTT enviados desde un bot de Telegram.
   - Los mensajes MQTT son cifrados con AES-256 en modo CBC.

### 2. **Bot de Telegram**
   - Se utiliza un bot de Telegram para interactuar con el ESP32 y controlar el estado del LED.
   - El bot permite a los usuarios encender y apagar el LED de manera remota.
   - El bot también se encarga de registrar los usuarios en una base de datos PostgreSQL para gestión y autenticación.

### 3. **Cifrado AES de Mensajes**
   - Se utiliza AES-256 con el modo CBC para cifrar los mensajes entre el ESP32 y el servidor Python.
   - La clave de cifrado y el vector de inicialización (IV) son fijos en el código para simplificar la implementación, pero en un entorno de producción, deberían ser dinámicos.

### 4. **Base de Datos PostgreSQL**
   - Los usuarios se registran en una base de datos PostgreSQL.
   - El sistema guarda los registros de los usuarios, incluidos los logs de acciones realizadas en el sistema.

## Configuración y Uso

1. **Configurar la Red Wi-Fi**:
   - Edita el archivo `red` dentro de la carpeta `micropython` con las credenciales de tu red Wi-Fi:
     ```json
     {
       "ssid": "nombreRed",
       "contrasena": "contraseñaRed"
     }
     ```

2. **Configurar el Bot de Telegram**:
   - Crea un bot en Telegram utilizando [BotFather](https://core.telegram.org/bots#botfather).
   - Obtén el `TOKEN` de tu bot y configúralo en el archivo `config.py` de la carpeta `pc`.

3. **Base de Datos**:
   - Crea una base de datos PostgreSQL y configura las credenciales en el archivo `base_datos.py` de la carpeta `pc`.

4. **Ejecutar el Proyecto**:
   - Ejecuta el código en el ESP32 con MicroPython.
   - Ejecuta el bot de Telegram en tu entorno local:
     ```bash
     python bot_telegram.py
     ```

5. **Controlar el LED**:
   - Usa el bot de Telegram para enviar comandos y controlar el LED del ESP32.
   - También puedes controlar el LED usando el botón físico conectado al ESP32.

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún error o deseas agregar nuevas funcionalidades, siéntete libre de abrir un *pull request*.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
from binascii import hexlify

import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, ConversationHandler, filters
from mqtt_BD import consultar_usuario_por_email, insertar_usuario, insertar_log
from mqtt_telegram import publicar_estado, conectar_mqtt, on_message, on_disconnect, on_connect

#CONFIGURACION TELEGRAM


TOKEN = "TELEGRAM_BOT_TOKEN"  # ← Reemplazar con el token real en ejecución
CHAT_ID = "TELEGRAM_CHAT_ID"  # ← Reemplazar con el ID del chat real

# Define los estados de la conversación
EMAIL,EMAIL2, NOMBRE, ID_AUTENTICACION = range(4)

# Variables para almacenar el user_id y estado
autenticado = False
user_id_almacenado = None

async def procesar_mensaje_mqtt(update: Update, estado: int, client):
    """
    Procesa un mensaje y publica el estado en el broker MQTT.
    """
    usuario = update.effective_user.first_name
    estado_data = estado


    # Publicación al broker MQTT
    publicar_estado(client,{"estadoPin": estado_data})
    print(estado_data)

    # Respuesta al usuario en Telegram
    await update.message.reply_text(
        f"LED {'encendido' if estado == 0 else 'apagado'} por {usuario}. Estado enviado al tópico MQTT."
    )

async def encender_led(update: Update, context: CallbackContext, client):
    """encender
    Manejador para el comando /on: Enciende el LED.
    """
    if await verificar_id(update, context):
        user_id = context.user_data['user_id']  # Obtiene el ID autenticado
        await insertar_log(user_id, estado=0)
        await procesar_mensaje_mqtt(update, estado=0, client=client)


async def apagar_led(update: Update, context: CallbackContext, client):
    """
    Manejador para el comando /off: Apaga el LED.
    """
    if await verificar_id(update, context):
        user_id = context.user_data['user_id']  # Obtiene el ID autenticado
        await insertar_log(user_id, estado=1)
        await procesar_mensaje_mqtt(update, estado=1, client=client)


async def consultar_estado(update: Update, context: CallbackContext):
    """Maneja el comando /estado para consultar el estado del LED."""
    await update.message.reply_text("El estado del LED no está disponible en este momento.")

async def bienvenida(update: Update, context: CallbackContext):
    """Envía un mensaje de bienvenida al iniciar el bot."""
    await update.message.reply_text(
        "¡Bienvenido al Bot de Telegram!\n"
        "Por favor valida tu identidad con el comando /ingresar\n"
        "o registrate con el comando /registrar. "
    )
async def get_chat_id(update: Update, context: CallbackContext):
    """Obtiene el ID del chat."""
    await update.message.reply_text(f"El ID de este chat es: {update.effective_chat.id}")

async def solicitar_id(update: Update, context: CallbackContext):
    """Solicita el ID de usuario antes de ejecutar /on y /off."""
    await update.message.reply_text("Por favor ingresa tu ID de usuario para continuar.")

async def verificar_id(update: Update, context: CallbackContext):
    """Verifica si el ID del usuario coincide con el autenticado."""
    if 'user_id' not in context.user_data:
        await update.message.reply_text("Debes autenticarte primero con /ingresar.")
        return False

    user_id = context.user_data['user_id']
    if user_id:
        await update.message.reply_text("ID verificado. Ahora puedes usar los comandos /on y /off.")
        return True
    else:
        await update.message.reply_text("ID incorrecto. Intenta nuevamente.")
        return False


async def start(update: Update, context: CallbackContext):
    """Inicia la conversación de registro."""
    await update.message.reply_text("Por favor, ingresa tu email para registrarte.")
    return EMAIL

async def email(update: Update, context: CallbackContext):
    """Recibe el email del usuario."""
    email = update.message.text.strip()

    # Consultamos si el usuario ya está registrado
    if await consultar_usuario_por_email(email):
        await update.message.reply_text("Este email ya está registrado.")
        return ConversationHandler.END

    context.user_data['email'] = email  # Guardamos el email en el contexto del usuario
    await update.message.reply_text("Ahora, por favor ingresa tu nombre completo.")
    return NOMBRE


async def nombre(update: Update, context: CallbackContext):
    """Recibe el nombre del usuario y finaliza el registro."""
    nombre = update.message.text.strip()
    email = context.user_data['email']

    # Realizamos la inserción del usuario en la base de datos
    user_id = await insertar_usuario(nombre, email)

    await update.message.reply_text(f"¡Gracias {nombre}! Te has registrado correctamente.")
    return ConversationHandler.END

async def cancelar(update: Update, context: CallbackContext):
    """Cancela el proceso de registro."""
    await update.message.reply_text("El proceso de registro ha sido cancelado.")
    return ConversationHandler.END

async def ingresar(update: Update, context: CallbackContext):
    """Inicia sesión de un usuario."""
    await update.message.reply_text("Por favor, ingresa tu email para autenticarte.")
    return EMAIL2


async def procesar_email(update: Update, context: CallbackContext):
    """Procesa el email del usuario para autenticar."""
    email = update.message.text.strip()

    try:
        result = await consultar_usuario_por_email(email)  # Consultamos el usuario
    except Exception as e:
        await update.message.reply_text(f"Error al consultar el usuario: {e}")
        return ConversationHandler.END

    if result:
        user_id = result[0]  # Suponemos que devuelve una tupla (id, ...)
        context.user_data['user_id'] = user_id
        await update.message.reply_text(f"Autenticación exitosa. Tu ID es {user_id}. Ahora puedes usar los comandos /on y /off.")

        return ConversationHandler.END
    else:
        await update.message.reply_text("Autenticación rechazada. Usa el comando /registrar para registrarte.")
        return ConversationHandler.END

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
import mqtt_telegram
# from mqtt_BD import on_message_bd
from telegram_bot import (
    TOKEN, bienvenida, consultar_estado, get_chat_id, encender_led, apagar_led,
    email, nombre, cancelar, start, ingresar, EMAIL, NOMBRE, procesar_email, EMAIL2
)

# -----------------------------------------------------------------------------
# Configuración de clientes MQTT y bot de Telegram
# -----------------------------------------------------------------------------

def configurar_mqtt(tipo_cliente):
    """
    Crea y configura un cliente MQTT según el tipo especificado.

    Args:
        tipo_cliente (str): Tipo de cliente (por ejemplo, 'telegram', 'base de datos').

    Returns:
        mqtt.Client: Cliente MQTT configurado y conectado.
    """
    client = mqtt_telegram.crear_cliente()
    id_mqtt = mqtt_telegram.asignar_mac(client)  # Se asigna un ID único usando la MAC
    mqtt_telegram.conectar_mqtt(client, tipo_cliente)
    return client


def configurar_bot(cliente):
    """
    Configura el bot de Telegram y sus comandos/conversaciones.

    Args:
        cliente: Cliente MQTT que se usará para enviar mensajes desde comandos del bot.

    Returns:
        Application: Aplicación de Telegram configurada con comandos y handlers.
    """
    app = Application.builder().token(TOKEN).build()

    # Handlers para comandos básicos
    app.add_handler(CommandHandler("start", bienvenida))
    app.add_handler(CommandHandler("estado", consultar_estado))
    app.add_handler(CommandHandler("help", bienvenida))  # Alias de /start
    app.add_handler(CommandHandler("id", get_chat_id))
    app.add_handler(CommandHandler("on", lambda update, context: encender_led(update, context, cliente)))
    app.add_handler(CommandHandler("off", lambda update, context: apagar_led(update, context, cliente)))

    # Conversación: registro de usuario
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('registrar', start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    ))

    # Conversación: ingreso por correo electrónico
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('ingresar', ingresar)],
        states={
            EMAIL2: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_email)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    ))

    return app

# -----------------------------------------------------------------------------
# Función principal: inicializa MQTT y el bot
# -----------------------------------------------------------------------------

def main():
    """
    Función principal que configura los clientes MQTT, las callbacks y arranca
    el bot de Telegram.
    """
    try:
        # Crear y conectar clientes MQTT
        clientMQTT = configurar_mqtt("telegram")
        clientBDD = configurar_mqtt("base de datos")

        # Configurar el bot de Telegram y asociar el cliente MQTT principal
        app = configurar_bot(clientMQTT)

        # Callbacks del cliente MQTT para el bot
        clientMQTT.on_message = mqtt_telegram.on_message
        clientMQTT.on_disconnect = mqtt_telegram.on_disconnect
        clientMQTT.on_connect = mqtt_telegram.on_connect

        # Callbacks del cliente MQTT para la base de datos (comentadas por ahora)
        # clientBDD.on_message = on_message_bd
        # clientBDD.on_disconnect = mqtt_telegram.on_disconnect
        # clientBDD.on_connect = mqtt_telegram.on_connect

        # Iniciar bucles de escucha MQTT
        clientMQTT.loop_start()
        clientBDD.loop_start()

        # Iniciar polling del bot de Telegram
        print("Bot de Telegram iniciado. Esperando comandos...")
        app.run_polling()

    except Exception as e:
        # Captura cualquier excepción durante la ejecución del programa
        print(f"Error en la aplicación principal: {e}")

# -----------------------------------------------------------------------------
# Punto de entrada del script
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

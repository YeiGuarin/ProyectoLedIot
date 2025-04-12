import datetime
import psycopg2
import re

# -----------------------------------------------------------------------------
# Conexión a la base de datos PostgreSQL
# -----------------------------------------------------------------------------

def conectar():
    """
    Establece la conexión con la base de datos PostgreSQL.

    Returns:
        conexión (psycopg2.connection): Objeto de conexión a la base de datos o None si falla.
    """
    try:
        conexion = psycopg2.connect(
            user="postgres",
            password="password",
            host="127.0.0.1",
            port="5432",
            database="bd"
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Conexión global para consultas posteriores
conn = conectar()

# -----------------------------------------------------------------------------
# Funciones asincrónicas de operación con la base de datos
# -----------------------------------------------------------------------------

async def consultar_usuario_por_email(email):
    """
    Consulta si existe un usuario con el correo electrónico proporcionado.

    Args:
        email (str): Correo electrónico del usuario a consultar.

    Returns:
        tuple | None: Resultado de la consulta o None si no se encontró o hubo un error.
    """
    print(email)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE correo_electronico = %s", (email,))
        result = cur.fetchone()
    except Exception as e:
        print(f"Error al consultar usuario por email: {e}")
        result = None
    finally:
        cur.close()
    return result


async def insertar_usuario(name, email):
    """
    Inserta un nuevo usuario en la base de datos.

    Args:
        name (str): Nombre del usuario.
        email (str): Correo electrónico del usuario.

    Returns:
        int | None: ID del usuario insertado o None si ocurrió un error.
    """
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, correo_electronico) VALUES (%s, %s) RETURNING id",
            (name, email)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    except psycopg2.Error as e:
        print(f"Error al insertar usuario: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()


async def insertar_log(user_id, estado):
    """
    Inserta un registro de log asociado a un usuario.

    Args:
        user_id (int): ID del usuario asociado.
        estado (str): Estado o evento a registrar.
    """
    print(f"Insertando log para el usuario {user_id} con estado {estado}")  # Debug
    cur = conn.cursor()
    query = """
        INSERT INTO public.logs (estado, dispositivo, id_usuario)
        VALUES (%s, %s, %s)
    """
    values = (estado, "telegram", user_id)

    try:
        print(f"Valores a insertar: {values}")  # Debug
        cur.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Error al insertar log: {e}")
    finally:
        cur.close()


async def obtener_id_por_nombre(nombre_usuario):
    """
    Busca el ID de un usuario por su nombre.

    Args:
        nombre_usuario (str): Nombre del usuario.

    Returns:
        int | None: ID del usuario si se encuentra, o None si no existe o falla.
    """
    cur = conn.cursor()

    try:
        query = "SELECT id FROM public.users WHERE nombre = %s LIMIT 1"
        cur.execute(query, (nombre_usuario,))
        result = cur.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error al buscar el ID por nombre: {e}")
        return None
    finally:
        cur.close()

# -----------------------------------------------------------------------------
# Validación de formato de correo electrónico
# -----------------------------------------------------------------------------

def es_email_valido(email):
    """
    Verifica si un email tiene un formato válido.

    Args:
        email (str): Dirección de correo electrónico.

    Returns:
        bool: True si el formato es válido, False en caso contrario.
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

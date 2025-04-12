from binascii import hexlify, unhexlify

# -----------------------------------------------------------------------------
# Conversiones entre datos binarios y cadenas en formato hexadecimal.
# Estas funciones son útiles en contextos donde se necesita representar,
# almacenar o transmitir datos binarios de manera legible o segura (por ejemplo,
# en protocolos de red, criptografía o almacenamiento de configuraciones).
# -----------------------------------------------------------------------------

def convert_to_hex(data: bytes) -> str:
    """
    Convierte datos binarios (bytes) a una cadena hexadecimal (str).

    Esta función es útil para representar datos binarios en un formato legible
    y fácilmente transmisible.

    Args:
        data (bytes): Los datos binarios a convertir.

    Returns:
        str: Representación hexadecimal de los datos binarios.
    """
    return hexlify(data).decode()


def convert_from_hex(hex_string: str) -> bytes:
    """
    Convierte una cadena hexadecimal a su representación binaria (bytes).

    Valida que la longitud de la cadena sea par, ya que cada byte se representa
    con dos caracteres hexadecimales.

    Args:
        hex_string (str): Cadena que representa los datos en hexadecimal.

    Raises:
        ValueError: Si la longitud de la cadena es impar.

    Returns:
        bytes: Datos binarios resultantes de la conversión.
    """
    if len(hex_string) % 2 != 0:
        raise ValueError("La cadena hexadecimal tiene longitud impar")
    return unhexlify(hex_string)


def is_valid_hex(hex_string: str) -> bool:
    """
    Verifica si una cadena es una representación hexadecimal válida.

    Se comprueba que la longitud sea par y que todos los caracteres sean
    válidos dentro del alfabeto hexadecimal.

    Args:
        hex_string (str): Cadena a validar.

    Returns:
        bool: True si la cadena es válida como hexadecimal, False en caso contrario.
    """
    if len(hex_string) % 2 != 0:
        return False

    try:
        bytes.fromhex(hex_string)  # Intento de conversión directa
        return True
    except ValueError:
        return False  # La conversión falló: contiene caracteres no hexadecimales.


def convert_to_bytes(hex_string: str) -> bytes:
    """
    Convierte una cadena hexadecimal a datos binarios (bytes),
    manejando explícitamente posibles errores de formato.

    Args:
        hex_string (str): Cadena hexadecimal que se desea convertir.

    Raises:
        ValueError: Si la cadena no tiene un formato hexadecimal válido.

    Returns:
        bytes: Datos binarios correspondientes a la cadena proporcionada.
    """
    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        raise ValueError(f"Formato hexadecimal inválido: {hex_string}") from e

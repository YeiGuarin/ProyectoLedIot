from binascii import hexlify, unhexlify
import hashlib
import os

# Se importa la biblioteca de criptografía moderna para operaciones AES
# Se ha comentado una alternativa con 'Crypto.Cipher', pero se utiliza la recomendada: 'cryptography'
# from Crypto.Cipher import AES
from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# -----------------------------------------------------------------------------
# Configuración de cifrado
# -----------------------------------------------------------------------------

ENCRYPTION_PASSWORD = "especializacion"  # Contraseña de entrada (no utilizada directamente como clave AES)

# -----------------------------------------------------------------------------
# Funciones auxiliares para manejo de cifrado AES-256 en modo CBC
# -----------------------------------------------------------------------------

def generate_key(password):
    """
    Genera una clave AES-256 a partir de una entrada fija.
    Actualmente, ignora la contraseña proporcionada y utiliza una cadena constante.

    Args:
        password (str): Contraseña de entrada (no utilizada en esta versión).

    Returns:
        bytes: Clave de 256 bits derivada usando SHA-256.
    """
    return hashlib.sha256(b'0123456789ABCDEF').digest()


def generate_iv():
    """
    Genera un IV (vector de inicialización) fijo.

    Nota: En una implementación segura, este IV debería ser aleatorio y diferente
    para cada operación de cifrado.

    Returns:
        bytes: IV de 128 bits utilizado en modo CBC.
    """
    return b'0123456789ABCDEF'


def unpad(data):
    """
    Elimina el padding aplicado al texto plano durante el cifrado.

    Args:
        data (bytes): Datos con padding.

    Returns:
        bytes: Datos sin padding.
    """
    padding_len = data[-1]
    return data[:-padding_len]


def aes_encrypt(key, iv, data):
    """
    Cifra los datos usando AES-256 en modo CBC con padding PKCS7.

    Args:
        key (bytes): Clave AES de 256 bits.
        iv (bytes): Vector de inicialización de 128 bits.
        data (bytes): Texto plano a cifrar.

    Returns:
        bytes: Datos cifrados (ciphertext).
    """
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    plaintext_padded = padder.update(data) + padder.finalize()

    ciphertext = encryptor.update(plaintext_padded) + encryptor.finalize()
    return ciphertext


def aes_decrypt(key, iv, data):
    """
    Descifra datos cifrados con AES-256 en modo CBC con padding PKCS7.

    Args:
        key (bytes): Clave AES utilizada para el cifrado.
        iv (bytes): Vector de inicialización utilizado.
        data (bytes): Datos cifrados.

    Returns:
        bytes: Texto plano descifrado.
    """
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    plaintext_padded = decryptor.update(data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    return unpadder.update(plaintext_padded) + unpadder.finalize()


def encrypt(data, password):
    """
    Cifra un texto dado utilizando una contraseña como base para la clave AES.

    Args:
        data (str): Texto plano a cifrar.
        password (str): Contraseña de entrada (no se usa en la clave actualmente).

    Returns:
        bytes: Datos cifrados.
    """
    key = generate_key(password)
    iv = generate_iv()
    plaintext_bytes = data.encode('utf-8')
    return aes_encrypt(key, iv, plaintext_bytes)


def decrypt(encrypted_data, password):
    """
    Descifra datos utilizando AES-256 en modo CBC con clave e IV fijos.

    Args:
        encrypted_data (bytes): Datos cifrados.
        password (str): Contraseña de entrada (no se usa en esta versión).

    Returns:
        str: Texto plano descifrado.
    """
    key = generate_key(password)
    iv = b'0123456789ABCDEF'
    decrypted_text = aes_decrypt(key, iv, encrypted_data)
    return decrypted_text.decode('utf-8')


# -----------------------------------------------------------------------------
# Ejecución principal (solo si el archivo se ejecuta directamente)
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mensaje = "Mensaje secreto"
    print("Texto original:", mensaje)

    try:
        # Encriptar el mensaje y convertir el resultado a cadena hexadecimal
        datos_cifrados = encrypt(mensaje, ENCRYPTION_PASSWORD)
        datos_cifrados_hex = hexlify(datos_cifrados).decode()
        print("Datos cifrados en hexadecimal:", datos_cifrados_hex)

        # Convertir de vuelta a binario y desencriptar el mensaje
        datos_cifrados_bin = unhexlify(datos_cifrados_hex)
        mensaje_descifrado = decrypt(datos_cifrados_bin, ENCRYPTION_PASSWORD)
        print("Mensaje descifrado:", mensaje_descifrado)

    except Exception as e:
        # Captura y muestra cualquier excepción que ocurra durante el proceso
        print(f"Error: {e}")

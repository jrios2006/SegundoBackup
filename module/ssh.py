#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ssh.py
======
Módulo de conexión y gestión de archivos en servidores **SFTP** usando la
librería `paramiko`.

Este módulo centraliza todas las operaciones necesarias para la comunicación
con un servidor SFTP remoto, incluyendo conexión, subida, descarga,
verificación, borrado y listado de archivos.

Funcionalidades principales:
- Establecer y cerrar conexiones SFTP.
- Crear carpetas remotas.
- Subir y descargar ficheros.
- Eliminar ficheros del servidor.
- Listar ficheros con o sin atributos extendidos.
- Verificar la existencia de ficheros.

El módulo está diseñado para ser invocado desde el script principal `main.py`
y desde otros componentes del proyecto.

Dependencias:
- paramiko
- logging
- os, datetime, sys

Ejemplo de uso básico:
    >>> from module.ssh import DescargarArchivoSFTP
    >>> cred = ["host.com", 22, "usuario", "clave", "", ""]
    >>> DescargarArchivoSFTP(cred, "data.csv", "/remoto/", "C:/local/data.csv")

Autor: [Tu nombre o equipo]
Versión: 1.0
"""
import logging
import sys
import os
import datetime
import paramiko

logger = logging.getLogger(__name__)

def conectar_sftp(credenciales):
    """
    Establece la conexión con el servidor SFTP usando credenciales.

    Args:
        credenciales (list): Lista con los parámetros de conexión en este orden:
            [servidor, puerto, usuario, clave, clave_privada, pass_clave_privada]

    Returns:
        tuple: (sftp, transport)
            - sftp (paramiko.SFTPClient): Cliente SFTP activo.
            - transport (paramiko.Transport): Transporte activo que debe cerrarse.
    """
    sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_passclaveprivada = credenciales
    transport = paramiko.Transport((sftp_servidor, sftp_puerto))
    if os.path.isfile(sftp_claveprivada):
        transport.connect(username=sftp_usuario, pkey=paramiko.RSAKey.from_private_key_file(sftp_claveprivada, password=sftp_passclaveprivada or None))
    else:
        transport.connect(username=sftp_usuario, password=sftp_clave)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport


def CrearCarpetaSFTP(credenciales, ruta):
    """
    Crea una carpeta en el servidor SFTP si no existe.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        ruta (str): Carpeta remota a crear.

    Returns:
        bool: True si la carpeta se creó, False si ya existía o hubo error.
    """
    Aux = False
    try:
        sftp, transport = conectar_sftp(credenciales)
        try:
            sftp.stat(ruta)
            #logger.warning(f"La carpeta {ruta} ya existe en {credenciales[0]}")
        except FileNotFoundError:
            sftp.mkdir(ruta)
            Aux = True
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo conectar con el servidor {credenciales[0]} con el usuario {credenciales[2]}"
        logger.error(Cadena)
        logger.error(e)
    return Aux


def SubirFicheroSFTP(credenciales, carpeta, fichero, nombrefichero):
    """
    Sube un archivo local al servidor SFTP.
    Si la carpeta remota no existe, la crea automáticamente.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        carpeta (str): Carpeta remota donde subir el archivo (sin '/' al final).
        fichero (str): Ruta local del archivo a subir.
        nombrefichero (str): Nombre con el que se guardará en el servidor.

    Returns:
        bool: True si el archivo se subió correctamente, False en caso de error.
    """
    Aux = False
    try:
        CrearCarpetaSFTP(credenciales, carpeta)
        sftp, transport = conectar_sftp(credenciales)
        remoteFilePath = carpeta + "/" + nombrefichero
        sftp.put(fichero, remoteFilePath)
        Aux = True
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo subir al servidor {credenciales[0]} el fichero {fichero}"
        logger.error(Cadena)
        logger.error(e)
    return Aux


def BorrarFicheroSFTP(credenciales, carpeta, fichero):
    """
    Borra un archivo del servidor SFTP.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        carpeta (str): Carpeta remota donde está el archivo.
        fichero (str): Nombre del archivo a borrar.

    Returns:
        bool: True si se borró correctamente, False en caso contrario.
    """
    Aux = False
    try:
        sftp, transport = conectar_sftp(credenciales)
        remoteFile = carpeta + "/" + fichero
        try:
            sftp.remove(remoteFile)
            Aux = True
        except FileNotFoundError:
            Cadena = f"No puedo borrar el fichero {fichero} de la carpeta {carpeta} en el servidor {credenciales[0]}"
            logger.warning(Cadena)
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo conectar con el servidor {credenciales[0]} con el usuario {credenciales[2]}"
        logger.error(Cadena)
        logger.error(e)
    return Aux


def ListarArchivosSFTP(credenciales, carpeta):
    """
    Lista los archivos contenidos en una carpeta remota.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        carpeta (str): Carpeta remota a listar.

    Returns:
        tuple:
            - bool: True si la conexión fue exitosa.
            - list: Lista con los nombres de archivos (vacía si no hay nada).
    """
    Aux = False
    ListaFicheros = []
    try:
        sftp, transport = conectar_sftp(credenciales)
        ListaFicheros = sftp.listdir(carpeta)
        Aux = True
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo conectar con el servidor {credenciales[0]} con el usuario {credenciales[2]}"
        logger.error(Cadena)
        logger.error(e)
    return Aux, ListaFicheros


def DescargarArchivoSFTP(credenciales, archivo, ruta='/', destino_local=None):
    """
    Descarga un archivo desde el servidor SFTP a la carpeta local especificada.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        archivo (str): Nombre del archivo remoto a descargar.
        ruta (str, opcional): Carpeta remota donde está el archivo. Default '/'.
        destino_local (str, opcional): Ruta local completa donde guardar el archivo.
            Si no se indica, se descargará en el directorio actual del programa.

    Returns:
        tuple:
            - bool: True si la descarga fue exitosa, False en caso de error.
            - str: Ruta local del archivo descargado (vacía si falló).
    """
    Aux = False
    NombreFicheroLocal = ''
    try:
        sftp, transport = conectar_sftp(credenciales)

        # Construir la ruta remota
        remoteFile = os.path.join(ruta, archivo).replace("\\", "/")

        # Si no se especifica destino_local, usar el directorio actual
        if destino_local is None:
            destino_local = os.path.join(os.getcwd(), archivo)
        else:
            # Asegurarse de que exista la carpeta destino
            os.makedirs(os.path.dirname(destino_local), exist_ok=True)

        # Descargar el archivo
        sftp.get(remoteFile, destino_local)

        Aux = True
        NombreFicheroLocal = destino_local

        sftp.close()
        transport.close()

    except Exception as e:
        Cadena = f"No consigo descargar el fichero {archivo} del servidor {credenciales[0]}"
        logger.error(Cadena)
        logger.error(e)

    return Aux, NombreFicheroLocal


def VerificarFicheroSFTP(credenciales, archivo, ruta='/'):
    """
    Verifica si un archivo existe en el servidor SFTP.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        archivo (str): Nombre del archivo a verificar.
        ruta (str, opcional): Carpeta remota donde buscar. Default '/'.

    Returns:
        bool: True si el archivo existe, False si no existe o hay error.
    """
    Aux = False
    try:
        sftp, transport = conectar_sftp(credenciales)
        remoteFile = ruta + "/" + archivo
        try:
            sftp.stat(remoteFile)
            Aux = True
        except FileNotFoundError:
            Aux = False
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo conectar con el servidor {credenciales[0]} con el usuario {credenciales[2]}"
        logger.error(Cadena)
        logger.error(e)
    return Aux


def ListarArchivosSFTPconAtributos(credenciales, carpeta):
    """
    Lista los archivos de una carpeta con sus atributos
    (tamaño, fechas, permisos, etc.), ordenados por fecha de modificación.

    Args:
        credenciales (list): Lista con los parámetros de conexión.
        carpeta (str): Carpeta remota a listar.

    Returns:
        tuple:
            - bool: True si la conexión fue exitosa.
            - list: Lista de diccionarios con atributos de cada archivo.
    """
    Aux = False
    Lista = []
    try:
        sftp, transport = conectar_sftp(credenciales)
        archivos = sftp.listdir_attr(carpeta)
        archivos.sort(key=lambda x: x.st_mtime, reverse=True)
        for atributos in archivos:
            diccionario_atributos = {
                'nombre': atributos.filename,
                'size': atributos.st_size,
                'uid': atributos.st_uid,
                'gid': atributos.st_gid,
                'mode': atributos.st_mode,
                'atime': datetime.datetime.fromtimestamp(atributos.st_atime),
                'mtime': datetime.datetime.fromtimestamp(atributos.st_mtime)
            }
            Lista.append(diccionario_atributos)
        Aux = True
        sftp.close()
        transport.close()
    except Exception as e:
        Cadena = f"No consigo conectar con el servidor {credenciales[0]} con el usuario {credenciales[2]}"
        logger.error(Cadena)
        logger.error(e)
    return Aux, Lista

"""
files.py
=========
Módulo auxiliar para operaciones de gestión de archivos locales
y utilidades relacionadas con el sincronizador SFTP.

Responsabilidades principales:
- Localizar subcarpetas finales dentro de una estructura de directorios.
- Determinar el fichero más reciente en un directorio remoto (vía SFTP).
- Eliminar versiones antiguas de archivos locales, conservando solo la más reciente.

Este módulo no realiza conexiones SFTP ni configuraciones de logging;
solo usa el logger global configurado desde el módulo principal.

Dependencias:
- os (operaciones de sistema de archivos)
- logging (para registrar eventos de eliminación o errores)

Ejemplo de uso:
    >>> from module.files import listar_subcarpetas, eliminar_antiguos
    >>> carpetas = listar_subcarpetas("C:/clientes")
    >>> eliminados = eliminar_antiguos("C:/clientes/empresa1", "fichero_nuevo.csv")

Autor: [Tu nombre o equipo]
Versión: 1.0
"""
import os
import logging

logger = logging.getLogger(__name__)

def listar_subcarpetas(base_path):
    """
    Devuelve una lista con todas las carpetas finales dentro de base_path
    (aquellas que no contienen subcarpetas).

    Args:
        base_path (str): Ruta base a recorrer.

    Returns:
        list: Lista de rutas absolutas de carpetas finales.
    """
    subcarpetas = []
    for root, dirs, files in os.walk(base_path):
        if not dirs:  # Solo carpetas finales
            subcarpetas.append(root)
    return subcarpetas


def fichero_mas_reciente(sftp, remote_dir):
    """
    Obtiene el fichero más reciente en un directorio remoto SFTP.

    Args:
        sftp (paramiko.SFTPClient): Conexión SFTP activa.
        remote_dir (str): Ruta remota a analizar.

    Returns:
        SFTPAttributes | None: El archivo más reciente o None si no hay.
    """
    try:
        files = sftp.listdir_attr(remote_dir)
        if not files:
            return None
        return max(files, key=lambda f: f.st_mtime)
    except Exception as e:
        logger.error(f"Error buscando fichero más reciente en {remote_dir}: {e}")
        return None


def eliminar_antiguos(carpeta, ultimo_fichero):
    """
    Elimina todos los ficheros de una carpeta excepto el especificado.

    Args:
        carpeta (str): Ruta local donde se eliminarán los archivos antiguos.
        ultimo_fichero (str): Nombre del fichero que se debe conservar.

    Returns:
        int: Número de ficheros eliminados.
    """
    eliminados = 0
    try:
        for fichero in os.listdir(carpeta):
            ruta = os.path.join(carpeta, fichero)
            if os.path.isfile(ruta) and fichero != ultimo_fichero:
                os.remove(ruta)
                eliminados += 1
                logger.info(f"Eliminado fichero antiguo: {ruta}")
    except Exception as e:
        logger.error(f"Error eliminando ficheros antiguos en {carpeta}: {e}")
    return eliminados

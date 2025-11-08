"""
main.py
========
Script principal del proyecto **Sincronizador de archivos SFTP**.

Este módulo orquesta el flujo de sincronización entre un servidor remoto SFTP y
un conjunto de carpetas locales. Se encarga de:

1. Cargar los parámetros de configuración y credenciales desde JSON.
2. Configurar el sistema de logging con rotación.
3. Localizar las subcarpetas finales del directorio local.
4. Conectarse al servidor SFTP, listar los archivos remotos y descargar el más reciente.
5. Eliminar versiones antiguas de los ficheros locales, manteniendo solo la más reciente.
6. Registrar todo el proceso y mostrar un resumen global al finalizar.

---

Dependencias:
- Paramiko (para la conexión SFTP)
- Módulos locales:
  - `module.logging_config`
  - `module.ssh`
  - `module.files`

Ejemplo de ejecución:
    >>> python main.py

Autor: [Tu nombre o equipo]
Versión: 1.0
"""
import os
import json
import logging
import time
from module.logging_config import configurar_logger
from module.ssh import conectar_sftp, ListarArchivosSFTPconAtributos, DescargarArchivoSFTP
from module.files import listar_subcarpetas, eliminar_antiguos


def cargar_json(path):
    """
    Carga un archivo JSON y devuelve su contenido como diccionario.

    Args:
        path (str): Ruta absoluta o relativa al archivo JSON.

    Returns:
        dict: Contenido del JSON parseado.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        json.JSONDecodeError: Si el contenido no es un JSON válido.
    """    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """
    Función principal del sincronizador SFTP.

    Flujo general:
    1. Carga de configuración y credenciales.
    2. Configuración del sistema de logging.
    3. Detección de subcarpetas locales a procesar.
    4. Para cada carpeta:
        - Construye la ruta remota equivalente.
        - Lista los archivos remotos y determina el más reciente.
        - Descarga el archivo si no existe localmente.
        - Elimina versiones antiguas locales.
    5. Al finalizar, genera un resumen con estadísticas globales.

    El proceso se detalla paso a paso en el log principal.
    """    
    inicio = time.time()  # Para calcular duración total

    # === 1️⃣ Cargar configuración ===
    config_path = "config/config.json"
    credenciales_path = "config/credenciales.json"

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"No se encuentra el archivo de configuración: {config_path}")
    if not os.path.exists(credenciales_path):
        raise FileNotFoundError(f"No se encuentra el archivo de credenciales: {credenciales_path}")

    config = cargar_json(config_path)
    credenciales = cargar_json(credenciales_path)["SFTP"]

    # === 2️⃣ Configurar logging ===
    logger = configurar_logger(config)
    logger.info("=== Inicio de ejecución del sincronizador de archivos ===")

    # === 3️⃣ Validar existencia del directorio base ===
    base_dir = config.get("directorio_local")
    if not base_dir or not os.path.isdir(base_dir):
        logger.error(f"El directorio base '{base_dir}' no existe o no es válido.")
        return

    # === 4️⃣ Obtener subcarpetas finales ===
    carpetas = listar_subcarpetas(base_dir)
    logger.info(f"Encontradas {len(carpetas)} carpetas finales para procesar.")

    # === Variables de resumen ===
    total_descargados = 0
    total_bytes_descargados = 0
    total_eliminados = 0
    carpetas_con_error = 0

    # === 5️⃣ Procesar cada carpeta ===
    for carpeta_local in carpetas:
        try:
            # Construir ruta remota equivalente
            base_dir_normalizado = os.path.normpath(base_dir)
            relativa = os.path.relpath(carpeta_local, base_dir_normalizado)
            ruta_remota = os.path.join(config.get("directorio_remoto", "/"), relativa).replace("\\", "/")

            logger.info(f"Procesando carpeta local '{carpeta_local}' con ruta remota '{ruta_remota}'")

            ok, archivos_remotos = ListarArchivosSFTPconAtributos(credenciales, ruta_remota)
            if not ok:
                logger.warning(f"No se pudo listar archivos en la ruta remota {ruta_remota}")
                carpetas_con_error += 1
                continue

            if not archivos_remotos:
                logger.info(f"No hay archivos remotos en {ruta_remota}")
                continue

            # Obtener el más reciente (ya ordenados por fecha desc)
            archivo_reciente = archivos_remotos[0]
            nombre_fichero = archivo_reciente["nombre"]
            tamano_bytes = archivo_reciente["size"]
            logger.info(f"Archivo más reciente en remoto: {nombre_fichero} ({tamano_bytes:,} bytes)")

            # Comprobar si ya existe localmente
            destino_local = os.path.join(carpeta_local, nombre_fichero)
            if os.path.exists(destino_local):
                logger.info(f"El fichero {nombre_fichero} ya existe localmente. No se descarga.")
            else:
                descargado, ruta_descargada = DescargarArchivoSFTP(
                    credenciales, nombre_fichero, ruta_remota, destino_local
                )
                if descargado:
                    total_descargados += 1
                    total_bytes_descargados += tamano_bytes
                    logger.info(f"Descargado correctamente {nombre_fichero} a {ruta_descargada}")
                else:
                    logger.warning(f"No se pudo descargar el fichero {nombre_fichero}")

            # Eliminar ficheros antiguos
            eliminados = eliminar_antiguos(carpeta_local, nombre_fichero)
            total_eliminados += eliminados
            if eliminados > 0:
                logger.info(f"{eliminados} ficheros antiguos eliminados en {carpeta_local}")
            else:
                logger.debug(f"No había ficheros antiguos que eliminar en {carpeta_local}")

        except Exception as e:
            carpetas_con_error += 1
            logger.error(f"Error procesando la carpeta {carpeta_local}: {e}")

    # === 6️⃣ Resumen final ===
    duracion = time.time() - inicio
    minutos, segundos = divmod(int(duracion), 60)
    logger.info("=== Resumen de ejecución ===")
    logger.info(f"Tiempo total de proceso: {minutos} min {segundos} seg")
    logger.info(f"Carpetas procesadas: {len(carpetas)}")
    logger.info(f"Ficheros descargados: {total_descargados}")
    logger.info(f"Bytes descargados: {total_bytes_descargados:,}")
    logger.info(f"Ficheros eliminados localmente: {total_eliminados}")
    logger.info(f"Carpetas con errores: {carpetas_con_error}")
    logger.info("=== Proceso finalizado correctamente ===")


if __name__ == "__main__":
    main()

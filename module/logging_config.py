"""
Módulo `logging_config`
-----------------------

Proporciona la configuración del sistema de logging para el proyecto,
permitiendo registrar información, advertencias y errores en un fichero
con rotación automática.

Características:
    - Logger centralizado con formato estándar de fecha, nivel y módulo.
    - Rotación de ficheros (tamaño máximo y número de copias configurables).
    - Carpeta de logs creada automáticamente si no existe.
    - Filtrado de mensajes de Paramiko para mostrar solo warnings y errores.

Dependencias:
    - logging
    - logging.handlers.RotatingFileHandler
    - os
"""
import logging
from logging.handlers import RotatingFileHandler
import os

def configurar_logger(config):
    """
    Configura el sistema de logging con un archivo rotativo y formateo estándar.

    Args:
        config (dict): Diccionario de configuración que puede incluir la sección "log"
            con los parámetros:
                - ruta_log (str): Ruta del archivo de log. Default: "logs/cliente.log".
                - max_megas (int): Tamaño máximo del archivo en megabytes antes de rotar.
                - copias (int): Número de archivos de backup a mantener.

    Returns:
        logging.Logger: Logger configurado listo para usar en todo el proyecto.

    Notas:
        - Los logs se escriben con formato: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        - Se evita la duplicación de handlers al reconfigurar.
        - Los mensajes de INFO de Paramiko se silencian; solo se muestran WARN y ERROR.
    
    Ejemplo:
        logger = configurar_logger(config)
        logger.info("Inicio del script")
        logger.error("Ha ocurrido un error")
    """
    log_cfg = config.get("log", {})
    ruta_log = log_cfg.get("ruta_log", "logs/sincronizar_archivos.log")
    max_megas = log_cfg.get("max_megas", 5)
    copias = log_cfg.get("copias", 5)

    # Asegurar que la carpeta del log existe
    os.makedirs(os.path.dirname(ruta_log), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Crear manejador con rotación
    handler = RotatingFileHandler(
        ruta_log,
        maxBytes=max_megas * 1024 * 1024,
        backupCount=copias,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Evitar duplicados
    if not logger.handlers:
        logger.addHandler(handler)
    
    # Silenciar INFO de paramiko, solo warnings y errores
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("paramiko.transport").setLevel(logging.WARNING)
    logging.getLogger("paramiko.transport.sftp").setLevel(logging.WARNING)

    return logger

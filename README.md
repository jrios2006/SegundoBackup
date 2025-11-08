# 🔄 Sincronizador de archivos SFTP

Proyecto en **Python** para verificar, sincronizar y mantener actualizados ficheros entre un servidor **SFTP remoto** y un **directorio local**, descargando automáticamente el fichero más reciente de cada subcarpeta y eliminando versiones antiguas.

---

## 📂 Estructura del proyecto

```bash
proyecto_inventario/
│
├── config/
│ ├── config.json # Parámetros generales (rutas locales/remotas, logging, opciones)
│ └── credenciales.json # Credenciales de conexión SFTP
│
├── module/
│ ├── init.py
│ ├── logging_config.py # Configuración de logs con rotación
│ ├── ssh.py # Funciones para conexión y operaciones SFTP
│ └── files.py # Utilidades de gestión de ficheros locales
│
├── main.py # Punto de entrada principal
└── README.md # Documentación del proyecto
```


---

## ⚙️ Configuración

### 📁 `config/config.json`

Ejemplo de configuración:

```json
{
  "directorio_local": "C:/segundobackup/clientes",
  "directorio_remoto": "/",
  "forzar_descarga": false,
  "mantener_ultimo": true,
  "log": {
    "ruta_log": "logs/sincronizar_archivos.log",
    "max_megas": 1,
    "copias": 2
  }
}


```

Parámetros principales:

* **directorio_local**: Carpeta base local donde se buscan las subcarpetas a sincronizar.
* **directorio_remoto**: Carpeta raíz del servidor SFTP desde donde se buscarán los ficheros.
* **forzar_descarga**: (reservado para futuras versiones).
* **mantener_ultimo**: Si es true, mantiene solo el último fichero descargado.
* **log**: Configuración de rotación de logs.

---

### 🔐 `config/credenciales.json`

Ejemplo de credenciales SFTP:

```json
{
  "SFTP": [
    "HOST_SFTP",
    2222,
    "user_SFTP",
    "pass_user",
    "",
    ""
  ]
}
```

Orden esperado:

```json
[ "servidor", "puerto", "usuario", "clave", "clave_privada", "pass_clave_privada" ]

```

---

🧩 Dependencias

El proyecto utiliza Paramiko para la conexión SFTP.

Instalar dependencias con:

```bash
pip install -r requirements.txt
```

---

▶️ Ejecución

Desde la raíz del proyecto:

El script:

1. Carga configuración y credenciales.
2. Busca subcarpetas finales dentro de directorio_local.
3. Construye la ruta remota equivalente en el servidor SFTP.
4. Lista los archivos disponibles y descarga el más reciente.
5. Elimina versiones antiguas locales, dejando solo la última.
6. Genera un log detallado con todo el proceso.

---

🪵 Logs

El log principal se genera en la ruta definida en `config.json` (por defecto: `logs/sincronizar_archivos.log`).

Formato de log:

```bash
YYYY-MM-DD HH:MM:SS [LEVEL] módulo: mensaje
```

El sistema de logging incluye rotación automática:
por tamaño (en MB) y número de copias, configurables desde el JSON.


📊 Resumen final del proceso

Al finalizar la ejecución, se muestra un resumen con métricas globales:

```bash
=== Resumen de ejecución ===
Tiempo total de proceso: 3 min 12 seg
Carpetas procesadas: 36
Ficheros descargados: 12
Bytes descargados: 2,345,887,621
Ficheros eliminados localmente: 11
Carpetas con errores: 2
=== Proceso finalizado correctamente ===
```

---

🕒 Ejecución automática (tarea programada)

El sincronizador puede ejecutarse de forma desatendida mediante una tarea programada del sistema operativo.
A continuación, se detallan las configuraciones recomendadas para Windows y Linux/macOS.


🪟 En Windows (Programador de tareas)

1. Abrir el programador de tareas
    * Pulsa Inicio → escribe Programador de tareas → Ábrelo.
2. Crear una nueva tarea
    * En el panel derecho, selecciona "Crear tarea...".
3. Pestaña General
    * Nombre: Sincronizador SFTP
    * Descripción: Descarga diaria de ficheros desde el servidor SFTP
    * Ejecutar tanto si el usuario ha iniciado sesión como si no.
    * Marcar: “Ejecutar con los privilegios más altos”.
4. Pestaña Desencadenadores
* Clic en “Nuevo…”.
    * Elegir cuándo ejecutar la tarea:
        * Por ejemplo: Diariamente a las 23:00.
    * Aceptar.
5. Pestaña Acciones
    * Clic en “Nuevo…”.
    * Acción: Iniciar un programa.
    * En “Programa o script”, escribe la ruta al intérprete de Python, por ejemplo:
    ```bash
    C:\Python311\python.exe
    ```
    * En “Agregar argumentos”, escribe:
    ```bash
    C:\SHP\sincronizador\main.py
    ```
    * En “Iniciar en”, pon el directorio donde está el script:
    ```bash
    C:\SHP\sincronizador
    ```
6. Pestaña Condiciones / Configuración
    * Desactiva la opción de “Iniciar solo si el equipo está enchufado” si lo deseas.
    * Marca “Ejecutar tarea lo antes posible si se omite una ejecución programada”.
7. Guardar la tarea
    * Acepta y, si lo pide, introduce las credenciales del usuario.

---

🐧 En Linux o macOS (cron job)

1. Abrir crontab
```bash
crontab -e
```
2. Añadir una línea de ejecución automática
Por ejemplo, para ejecutar todos los días a las 23:00:
```bash
0 23 * * * /usr/bin/python3 /home/usuario/sincronizador/main.py >> /home/usuario/sincronizador/logs/cron.log 2>&1
```
    Donde:
    * /usr/bin/python3 → ruta al intérprete de Python.
    * /home/usuario/sincronizador/main.py → ruta del script.
    * El operador >> redirige el log estándar y los errores (2>&1) al archivo cron.log.
3. Verificar que funciona
    * Espera a la hora programada o prueba manualmente:
    ```bash
    python3 /home/usuario/sincronizador/main.py
    ```


import signal
import subprocess
import sys
import time
import webbrowser

# pip install requests
# permite hacer fácilmente solicitudes HTTP (como GET, POST, PUT, DELETE) a servidores web, interactuando con APIs o sitios web para enviar y recibir datos. Es ampliamente utilizada para integraciones con servicios en línea.
import requests
# pip install plyer para las notificaciones de escritorio
from plyer import notification

# Constantes
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
DJANGO_COMMAND = [sys.executable, "manage.py", "runserver", "8555"]
DJANGO_URL = "http://127.0.0.1:8555"
RETRY_INTERVAL = 1  # segundos
CHECK_INTERVAL = 2  # segundos para verificar si el servidor sigue activo
MAX_RECONNECT_ATTEMPTS = 3  # número máximo de intentos de reconexión

server_process = None
running = True  # Control del monitoreo
reconnect_attempts = 0  # Conteo de reconexiones


def send_notification(title, message):
  """Envía una notificación de escritorio y la imprime en consola."""
  full_message = f"@Javic Soft Code\n{message}"
  notification.notify(
    title=title,
    message=full_message,
    timeout=3,
    app_icon=r"C:\Users\ingja\PycharmProjects\Icon_JavicSoftCode\JavicSoftCode.ico",
  )
  print(full_message)


def is_server_running(url=DJANGO_URL):
  """Verifica si el servidor está activo."""
  try:
    response = requests.get(url)
    return response.status_code == 200
  except requests.ConnectionError:
    return False
  except requests.RequestException as e:
    send_notification("Error de Conexión", f"Error al verificar el servidor: {e}")
    return False


def start_server():
  """Inicia el servidor de Django y abre el navegador."""
  global server_process, reconnect_attempts
  try:
    server_process = subprocess.Popen(DJANGO_COMMAND, shell=False)
    message = "Activando el servidor de Django..."
    send_notification("Iniciando Servidor", message)

    # Reintentos si el servidor no está activo
    while not is_server_running():
      reconnect_attempts += 1
      if reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
        message = f"Servidor no disponible, reintentando en {RETRY_INTERVAL} segundo(s)... (Intento {reconnect_attempts} de {MAX_RECONNECT_ATTEMPTS})"
        send_notification("Servidor Inactivo", message)
        time.sleep(RETRY_INTERVAL)
      else:
        message = "Servidor no disponible después de varios intentos. Deteniendo el script."
        send_notification("Error Crítico", message)
        stop_server(None, None)
        sys.exit(1)

    # Si el servidor está activo
    message = "El servidor de Django está activo."
    send_notification("Servidor Activo", message)
    webbrowser.register("brave", None, webbrowser.BackgroundBrowser(BRAVE_PATH))
    webbrowser.get("brave").open(DJANGO_URL)

    reconnect_attempts = 0  # Reinicia el conteo de reconexiones
    monitor_server()

  except FileNotFoundError as e:
    error_message = (
      f"Error: No se encontró el archivo o directorio especificado. {e}"
    )
    send_notification("Error de Archivo", error_message)
  except Exception as e:
    error_message = f"Error inesperado al iniciar el servidor: {e}"
    send_notification("Error Inesperado", error_message)


def stop_server(signum, frame):
  """Detiene el servidor de Django de manera segura."""
  global server_process, running
  running = False  # Detiene el monitoreo
  if server_process is not None:
    message = "Apagando el servidor de Django..."
    send_notification("Deteniendo Servidor", message)
    server_process.terminate()
    server_process.wait()
    send_notification("Servidor Detenido", "El servidor de Django ha sido apagado.")
  else:
    send_notification("Servidor Inactivo", "El servidor no está en ejecución.")


def monitor_server():
  """Monitorea continuamente el estado del servidor y lo reinicia si es necesario."""
  global running, reconnect_attempts
  try:
    while running:
      if not is_server_running():
        reconnect_attempts += 1
        message = f"El servidor de Django se ha detenido inesperadamente. Intento {reconnect_attempts} de {MAX_RECONNECT_ATTEMPTS}."
        send_notification("Servidor Detenido", message)

        if reconnect_attempts < MAX_RECONNECT_ATTEMPTS:
          restart_server()
        else:
          message = "Número máximo de intentos de reconexión alcanzado. Deteniendo el servidor."
          send_notification("Deteniendo Servidor", message)
          stop_server(None, None)
          sys.exit(
            1
          )  # Detener el script completamente si fallan los intentos
      time.sleep(CHECK_INTERVAL)
  except KeyboardInterrupt:
    send_notification(
      "Monitoreo Interrumpido", "Monitoreo interrumpido por el usuario."
    )
    stop_server(None, None)
  except Exception as e:
    error_message = f"Error inesperado en el monitoreo del servidor: {e}"
    send_notification("Error en Monitoreo", error_message)
    stop_server(None, None)


if __name__ == "__main__":
  signal.signal(signal.SIGINT, stop_server)
  signal.signal(signal.SIGTERM, stop_server)

  start_server()

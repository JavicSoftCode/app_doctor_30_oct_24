import os
import subprocess
import sys
import time

# pip install plyer para las notificaciones de escritorio
from plyer import notification

DJANGO_COMMAND = [sys.executable, "manage.py"]
# PROJECT_PATH = "Clinic"  # Ruta desde donde empieza tu proyecto


def send_notification(title, message):
    """Envía una notificación de escritorio y la imprime en consola."""
    full_message = f"@Javic Soft Code\n{message[:200]}"
    notification.notify(
        title=title,
        message=full_message,
        timeout=3,
        app_icon=r"C:\Users\ingja\PycharmProjects\Icon_JavicSoftCode\JavicSoftCode.ico",
    )
    print(full_message)
    time.sleep(3)  # Espera sincronizada de 3 segundos después de cada notificación


def run_command(command):
    """Ejecuta un comando en la terminal y maneja errores."""
    try:
        print(f"Ejecutando comando: {' '.join(command)}")
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando '{' '.join(command)}': {e.stderr}")
        return False, e.stderr


def run_migrations():
    """Ejecuta los comandos makemigrations y migrate."""
    print("\n\033[1;4;37m🔱 Aplicando... Comando Makemigrations.\033[0m\n")

    success, output = run_command([*DJANGO_COMMAND, "makemigrations"])

    if success:
        if "No changes" in output or "No migrations to apply" in output:
            send_notification(
                "Migraciones Anteriores",
                "✅ Migraciones realizadas anteriormente. No hay cambios nuevos.",
            )
            print("✅ Migraciones realizadas anteriormente. No hay cambios nuevos.")
        else:
            send_notification(
                "Migraciones Completadas", "✅ Makemigrations completado."
            )

        # Ejecutar migrate incluso si no hay nuevos cambios
        print("\033[1;4;37m⚜️  Aplicando... Comando Migrate\033[0m")
        success, output = run_command([*DJANGO_COMMAND, "migrate"])
        if success:
            send_notification("Migraciones Aplicadas", "✅ Migraciones completadas.")
        else:
            send_notification("Error Migrar", f"❌ Error al aplicar migrate: {output}")
    else:
        send_notification(
            "Error Makemigrations", f"❌ Error al realizar makemigrations: {output}"
        )


if __name__ == "__main__":
    print("🔱 Ejecutando comandos iniciales de makemigrations y migrate...")
    run_migrations()  # Ejecuta las migraciones al inicio

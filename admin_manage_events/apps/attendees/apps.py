# apps/attendees/apps.py
from django.apps import AppConfig


class AttendeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attendees'
    verbose_name = 'Asistentes'

    def ready(self):
        # activamos los signals
        import apps.attendees.signals  # Importar las señales

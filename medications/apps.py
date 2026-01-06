from django.apps import AppConfig
import os
import threading

class MedicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medications'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('LIARA_APP_NAME'):
            from .utils import run_mqtt_task, run_reminder_task
            
            threading.Thread(target=run_mqtt_task, daemon=True).start()
            
            threading.Thread(target=run_reminder_task, daemon=True).start()
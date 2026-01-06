import os
import threading
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

def start_background_tasks():
    try:
        from medications.utils import run_mqtt_task, run_reminder_task
        
        threading.Thread(target=run_mqtt_task, daemon=True).start()
        threading.Thread(target=run_reminder_task, daemon=True).start()
        print("✅ Background Tasks started from WSGI!")
    except Exception as e:
        print(f"❌ Failed to start background tasks: {e}")

if os.environ.get('RUN_MAIN') != 'true': 
    start_background_tasks()

application = get_wsgi_application()
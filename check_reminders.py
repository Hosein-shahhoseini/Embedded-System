import os
import django
import time
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from medications.models import Pill
from medications.notifications import send_push_to_all_devices

def check_and_send_reminders():
    now = timezone.now()
    overdue_pills = Pill.objects.filter(next_expected_intake__lte=now, count__gt=0)

    for pill in overdue_pills:
        if not pill.is_notified:
            title = "⏰ زمان مصرف دارو"
            message = f"نوبت مصرف قرص {pill.name} رسیده است."
            
            pill.is_notified = True 
            print(f"[{now.strftime('%H:%M:%S')}] First alarm sent.")
        else:
            title = "🔔 یادآوری مجدد"
            message = f"هنوز قرص {pill.name} را برنداشته‌اید!"
            print(f"[{now.strftime('%H:%M:%S')}] Reminder alarm sent.")

        send_push_to_all_devices(title, message)

        pill.next_expected_intake = now + timezone.timedelta(minutes=1)
        pill.save()

if __name__ == "__main__":
    print("🚀 Reminder Service Started (Testing 2min interval / 1min snooze)...")
    while True:
        try:
            check_and_send_reminders()
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(10)
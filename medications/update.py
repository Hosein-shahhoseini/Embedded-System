from datetime import datetime, timedelta
from .models import Pill, History

def check_medication_time():
    now = datetime.now()
    pills = Pill.objects.all()
    for pill in pills:
        if pill.last_taken:
            if pill.interval_unit == 'hour':
                next_dose = pill.last_taken + timedelta(hours=pill.interval_value)
            elif pill.interval_unit == 'minute':
                next_dose = pill.last_taken + timedelta(minutes=pill.interval_value)
            
            if now >= next_dose:
                print(f"NOTIFICATION: Time to take {pill.name} from container {pill.container_id}")

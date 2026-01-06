import os
import time
import ssl
import threading
import paho.mqtt.client as mqtt
from django.utils import timezone
from .models import Pill, History
from .notifications import send_push_to_all_devices

MQTT_BROKER = "p9869662.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883
MQTT_USER = "user1"
MQTT_PASS = "Pass1234"
MQTT_TOPIC = "esp32/pill_box/status"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CA_CERT_PATH = os.path.join(BASE_DIR, 'certs', 'emqxsl-ca.crt')


def run_reminder_task():
    print("🚀 Reminder Service Thread Started...")
    while True:
        try:
            now = timezone.now()
            overdue_pills = Pill.objects.filter(
                next_expected_intake__lte=now, 
                count__gt=0,
                is_active=True  
            )

            for pill in overdue_pills:
                if not pill.is_notified:
                    title = "⏰ زمان مصرف دارو"
                    message = f"نوبت مصرف قرص {pill.name} رسیده است."
                    pill.is_notified = True
                    print(f"[{now.strftime('%H:%M:%S')}] First alarm sent for {pill.name}")
                else:
                    title = "🔔 یادآوری مجدد"
                    message = f"هنوز قرص {pill.name} را برنداشته‌اید!"
                    print(f"[{now.strftime('%H:%M:%S')}] Snooze alarm sent for {pill.name}")

                send_push_to_all_devices(title, message)

                pill.next_expected_intake = now + timezone.timedelta(minutes=1)
                pill.save()
        
        except Exception as e:
            print(f"❌ Error in Reminder Task: {e}")
        
        time.sleep(15)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to Secured MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        if ':' not in payload: return

        action, c_id_str = payload.split(':')
        c_id = int(c_id_str)

        from .models import Pill, History
        
        pill = Pill.objects.filter(container_id=c_id).first()
        
        if not pill:
            print(f"❌ No Pill found for Container {c_id}")
            return

        if action == "ACTIVE":
            pill.is_active = True
            pill.save()
            message_text = f"محفظه {c_id + 1} ({pill.name}) اکنون فعال است."
            send_push_to_all_devices("محفظه فعال شد", message_text)
            print(f"🟢 Container {c_id} ({pill.name}) is now ACTIVE/FULL")

        elif action == "DEACTIVE":
            pill.is_active = False
            pill.save()
            message_text = f"محفظه {c_id + 1} ({pill.name}) اکنون غیر فعال است."
            send_push_to_all_devices("محفظه غیر فعال شد", message_text)
            print(f"🔴 Container {c_id} ({pill.name}) is now DEACTIVE/EMPTY")

        elif action == "PICKUP":
            if pill.count > 0:
                pill.count -= 1
                pill.update_next_intake() 
                
                History.objects.create(
                    pill=pill, 
                    pill_name=pill.name, 
                    count_after_intake=pill.count
                )
                
                message_text = f"قرص {pill.name} با موفقیت مصرف شد. موجودی: {pill.count}"
                send_push_to_all_devices("تایید مصرف دارو", message_text)
                print(f"Intake recorded for {pill.name}")
            else:
                print(f"⚠️ Container {c_id} is already 0!")
            pill.save() 

        elif action == "WARN":
            send_push_to_all_devices("⚠️ هشدار دستگاه", f"ظرف {pill.name} (شماره {c_id + 1}) برداشته شده اما سر جایش نیست!")
            print(f"🚨 Alarm for container {c_id}")

    except Exception as e:
        print(f"❌ MQTT Message Error: {e}")

def run_mqtt_task():
    print("📡 MQTT Thread Starting...")
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    
    if os.path.exists(CA_CERT_PATH):
        client.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_REQUIRED)
    else:
        print(f"⚠️ Warning: CA Cert not found at {CA_CERT_PATH}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"❌ MQTT Connection Error: {e}")
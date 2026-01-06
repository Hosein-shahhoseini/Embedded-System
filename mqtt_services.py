import paho.mqtt.client as mqtt
import ssl
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


from medications.models import Pill, History
from medications.notifications import send_push_to_all_devices
from django.utils import timezone


MQTT_BROKER = "p9869662.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883 
MQTT_USER = "user1"
MQTT_PASS = "Pass1234"
MQTT_TOPIC = "esp32/pill_box/status" 
CA_CERT_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'emqxsl-ca.crt')

active_pickups = {}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to Secured MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()        
        if ':' not in payload:
            print("⚠️ Invalid message format received, ignoring.")
            return
        c_id, action = payload.split(':')
        c_id = int(c_id)

        if action == "PICKUP":
            pill = Pill.objects.get(container_id=c_id)
            if pill.count > 0:
                pill.count -= 1
                pill.save()
                pill.update_next_intake()
                
                History.objects.create(
                    pill=pill, 
                    pill_name=pill.name, 
                    count_after_intake=pill.count
                )
                
                message_text = f"قرص {pill.name} با موفقیت مصرف شد. موجودی باقی‌مانده: {pill.count}"
                send_push_to_all_devices("تایید مصرف دارو", message_text)

                print(f"Intake recorded and notification triggered for {pill.name}")

        elif action == "WARN":
            send_push_to_all_devices("⚠️ هشدار دستگاه", f"ظرف شماره {c_id} برداشته شده اما سر جایش گذاشته نشده است!")
            print(f"🚨 Alarm received for container {c_id}")

    except Exception as e:
        print(f"Error: {e}")

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_REQUIRED)

client.on_connect = on_connect
client.on_message = on_message

print("🔄 Connecting to Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
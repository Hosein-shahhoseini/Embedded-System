import paho.mqtt.client as mqtt
import ssl
import os
import time

MQTT_BROKER = "p9869662.ala.asia-southeast1.emqxsl.com"
MQTT_PORT = 8883
MQTT_USER = "user1"
MQTT_PASS = "Pass1234"
MQTT_TOPIC = "esp32/pill_box/status"
CA_CERT_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'emqxsl-ca.crt')

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)

try:
    client.tls_set(ca_certs=CA_CERT_PATH, cert_reqs=ssl.CERT_REQUIRED)
except Exception as e:
    print(f"❌ Error loading certificate: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Simulator connected to Broker successfully!")
    else:
        print(f"❌ Connection failed with code {rc}")

client.on_connect = on_connect

print("🔄 Connecting to Broker...")
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

try:
    while True:
        print("\n" + "="*30)
        print("   💊 PILL BOX SIMULATOR   ")
        print("="*30)
        print("1. [PICKUP] Container 0 (Consume)")
        print("2. [PICKUP] Container 1 (Consume)")
        print("3. [WARN]   Container 0 (Not Returned)")
        print("4. [WARN]   Container 1 (Not Returned)")
        print("q. Quit")
        print("-" * 30)
        print("5. [ACTIVE]   Container 0")
        print("6. [DEACTIVE] Container 0")
        print("7. [ACTIVE]   Container 1")
        print("8. [DEACTIVE] Container 1")

        
        choice = input("Enter your choice: ").strip().lower()
        if choice == '1':
                payload = "PICKUP:0" 
                client.publish(MQTT_TOPIC, payload)
                print(f"🚀 Published: {payload}")
                
        elif choice == '2':
                payload = "PICKUP:1"
                client.publish(MQTT_TOPIC, payload)
                print(f"🚀 Published: {payload}")
                
        elif choice == '3':
                payload = "WARN:0"
                client.publish(MQTT_TOPIC, payload)
                print(f"🚨 Published Alert: {payload}")
                
        elif choice == '4':
                payload = "WARN:1"
                client.publish(MQTT_TOPIC, payload)
                print(f"🚨 Published Alert: {payload}")
        elif choice == '5':
            payload = "ACTIVE:0"
            client.publish(MQTT_TOPIC, payload)
            print(f"🚀 Published: {payload}")
            
        elif choice == '6':
            payload = "DEACTIVE:0"
            client.publish(MQTT_TOPIC, payload)
            print(f"🚀 Published: {payload}") 
        elif choice == '7':
            payload = "ACTIVE:1"
            client.publish(MQTT_TOPIC, payload)
            print(f"🚀 Published: {payload}") 
            
        elif choice == '8':
            payload = "DEACTIVE:1"
            client.publish(MQTT_TOPIC, payload)
            print(f"🚀 Published: {payload}") 
                
        elif choice == 'q':
            print("Exiting simulator...")
            break
        else:
            print("❌ Invalid choice, try again.")
        
        time.sleep(0.5)

finally:
    client.loop_stop()
    client.disconnect()
    print("👋 Simulator disconnected.")
from exponent_server_sdk import PushClient, PushMessage
from .models import ExpoPushToken

def send_push_to_all_devices(title, message):
    tokens = ExpoPushToken.objects.values_list('token', flat=True)
    
    if not tokens:
        print("No tokens found in database.")
        return

    client = PushClient()
    for token in tokens:
        try:
            push_message = PushMessage(to=token, title=title, body=message)
            client.publish(push_message)
            print(f"✅ Notification sent to {token}")
        except Exception as e:
            print(f"❌ Error sending to {token}: {e}")
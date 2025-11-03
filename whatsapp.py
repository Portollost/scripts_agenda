import requests
from config import WHATSAPP_API_URL, WHATSAPP_TOKEN

def get_headers():
    return {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

def enviar_mensagem(numero, texto):
    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    response = requests.post(WHATSAPP_API_URL, headers=get_headers(), json=payload)
    if response.status_code != 200:
        print(f"❌ Erro ao enviar mensagem para {numero}: {response.text}")
    else:
        print(f"✅ Mensagem enviada para {numero}")

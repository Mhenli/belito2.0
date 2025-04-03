import os
import requests
from fastapi import FastAPI, Request, HTTPException
from chatbot import AdvancedChatbot  # Importa tu chatbot

# Definir tu token de Telegram
TELEGRAM_BOT_TOKEN = "7871810780:AAG5tEHr-qMjZ-Q-tiOJHTiuHnhzCQCBUc0"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

app = FastAPI()
chatbot = AdvancedChatbot()

@app.post("/webhook")
async def receive_message(request: Request):
    """
    Recibe mensajes de Telegram y envía respuestas generadas por el chatbot.
    """
    try:
        data = await request.json()

        if "message" in data:
            chat_id = data["message"]["chat"]["id"]
            user_text = data["message"]["text"]

            # Obtener respuesta del chatbot
            respuesta = chatbot.buscar_respuesta_semantica(user_text)
            if not respuesta:
                respuesta = chatbot.generar_respuesta_ia(user_text)

            # Enviar respuesta a Telegram
            send_telegram_message(chat_id, respuesta)

        return {"status": "ok"}
    
    except Exception as e:
        # Si ocurre un error al procesar el mensaje, retorna el error
        raise HTTPException(status_code=500, detail=f"Error procesando el mensaje: {str(e)}")

def send_telegram_message(chat_id, text):
    """
    Envía un mensaje al usuario en Telegram.
    """
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)

        # Verificar si el mensaje se envió correctamente
        if response.status_code != 200:
            raise Exception(f"Error al enviar mensaje a Telegram: {response.text}")
        
    except Exception as e:
        # Si hay un error al enviar el mensaje, captura y muestra el error
        print(f"Error enviando mensaje a Telegram: {str(e)}")

@app.get("/")
def home():
    """
    Ruta de verificación.
    """
    return {"message": "Bot de Telegram funcionando correctamente"}



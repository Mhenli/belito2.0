from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from chatbot import AdvancedChatbot
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

chatbot = AdvancedChatbot()

class Message(BaseModel):
    text: str

@app.post("/chat")
def chat(message: Message):
    """
    Procesa la entrada del usuario y devuelve una respuesta basada en el contenido del PDF o, 
    si no hay coincidencias, genera una respuesta con IA.
    """

    respuesta = chatbot.buscar_respuesta_semantica(message.text)

    if not respuesta:
        respuesta = chatbot.generar_respuesta_ia(message.text)

    chatbot.log_interaccion(message.text, respuesta)
    return {"response": respuesta}

@app.get("/")
def home():
    """
    Ruta principal para verificar que el backend está corriendo correctamente.
    """
    return {"message": "¡Belito API funcionando!"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import psutil

def check_memory():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # Convierte a MB
    print(f"Uso de memoria: {mem:.2f} MB")

check_memory()

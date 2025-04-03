from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chatbot import AdvancedChatbot
import os
import traceback
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración para evitar problemas con el paralelismo de los tokenizadores
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI()

# Configuración de CORS (produce + dev)
origins = list(filter(None, [
    os.getenv("FRONTEND_URL"),
    os.getenv("FRONTEND_DEV")
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("CORS origins:", origins)

# Inicialización del chatbot
chatbot = AdvancedChatbot()

# Modelos de datos
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        print(f"📩 Mensaje recibido: {request.message}")  # Log para debug

        # Buscar respuesta semántica
        respuesta = chatbot.buscar_respuesta_semantica(request.message)

        # Si no hay respuesta semántica, generar con IA
        if not respuesta:
            respuesta = chatbot.generar_respuesta_ia(request.message)

        # Loguear la interacción
        chatbot.log_interaccion(request.message, respuesta)

        print(f"📤 Respuesta enviada: {respuesta}")  # Log de respuesta

        return {"response": respuesta}

    except Exception as e:
        traceback.print_exc()  # Muestra el error en consola
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.get("/")
def home():
    return {"message": "🚀 ¡Belito API funcionando correctamente!"}

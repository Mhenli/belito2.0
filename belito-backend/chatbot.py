import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class AdvancedChatbot:
    def __init__(self, json_file='documento.json', log_file='chatbot_log.json'):
        self.setup_logging(log_file)
        load_dotenv()
        self.text_data = self.load_json(json_file)  
        self.setup_language_model()
        self.setup_conversation_memory()

        if self.text_data:
            self.setup_semantic_search()
        else:
            print("⚠️ No se ha cargado texto del JSON.")

    def setup_logging(self, log_file):
        self.log_file = log_file
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_json(self, json_file):
        if not os.path.exists(json_file):
            print(f"⚠️ El archivo '{json_file}' no existe.")
            return []

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.articles = [{"title": item["article"], "content": item["content"]} for item in data]
            else:
                self.articles = [{"title": data["article"], "content": data["content"]}]

            print(f"✅ Cargados {len(self.articles)} artículos del JSON.")
            return self.articles
        except Exception as e:
            print(f"⚠️ Error cargando JSON: {e}")
            return []

    def setup_language_model(self):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("API key de OpenAI no encontrada")
            self.llm = OpenAI(temperature=0.7, openai_api_key=api_key, max_tokens=600)
            print("✅ Modelo de lenguaje configurado correctamente.")
        except Exception as e:
            raise Exception(f"❌ Error al configurar modelo de lenguaje: {e}")

    def setup_conversation_memory(self):
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(llm=self.llm, memory=self.memory, verbose=False)
        print("✅ Memoria de conversación configurada.")

    def setup_semantic_search(self):
        if not self.articles:
            print("⚠️ No hay artículos para procesar.")
            return

        print("🔍 Configurando búsqueda semántica...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.modelo = SentenceTransformer("all-MiniLM-L6-v2", device=device)
        self.fragmentos_texto = [art["content"] for art in self.articles]
        self.embeddings_fragmentos = self.modelo.encode(self.fragmentos_texto, convert_to_tensor=True)
        embeddings_np = np.array(self.embeddings_fragmentos.cpu().detach().numpy())
        self.index = faiss.IndexFlatL2(embeddings_np.shape[1])  
        self.index.add(embeddings_np)  
        print("✅ Índice FAISS configurado para búsqueda semántica.")

    def buscar_respuesta_semantica(self, user_input):
        if not hasattr(self, 'modelo'):
            print("⚠️ El modelo de búsqueda semántica no está inicializado.")
            return None

        embedding_pregunta = self.modelo.encode(user_input, convert_to_tensor=True)
        similitudes, indices = self.index.search(np.array([embedding_pregunta.cpu().detach().numpy()]), k=1)
        indice_mejor = indices[0][0]
        max_similitud = similitudes[0][0]

        print(f"🔍 Mejor coincidencia: índice {indice_mejor} | Similitud: {max_similitud:.4f}")

        if max_similitud < 0.5:
            print("⚠️ Similitud baja. Usando IA para generar respuesta.")
            return None

        fragmento_relevante = self.fragmentos_texto[indice_mejor]
        print(f"✅ Fragmento seleccionado: {fragmento_relevante[:200]}...")

        return self.refinar_respuesta(fragmento_relevante, user_input)

    def refinar_respuesta(self, fragmento, user_input):
        prompt = f"""
        Eres Belito, un asistente virtual de Belo. Responde de manera clara y amigable, usando emojis y formato atractivo.

        Fragmento relevante: 
        {fragmento}

        Pregunta:
        {user_input}

        Respuesta:
        """

        print("🧠 Prompt enviado a OpenAI:\n", prompt)  # 👈 esto te muestra si algo en el prompt está mal
        try:
            respuesta = self.llm.invoke(prompt)
            return respuesta.strip()  # 👈 así eliminás espacios vacíos al principio y fin
        except Exception as e:
            print(f"❌ Error refinando respuesta: {e}")
        return "Lo siento, hubo un problema al generar la respuesta con la información disponible."

    def generar_respuesta_ia(self, user_input):
        try:
            respuesta = self.conversation.predict(input=user_input)
            print(f"🤖 Respuesta IA: {respuesta}")
            return respuesta
        except Exception as e:
            print(f"❌ Error generando respuesta IA: {e}")
            return "Lo siento, hubo un problema generando mi respuesta."

    def chat(self):
        print("🤖 ¡Hola! Soy Belito, tu asistente virtual. Escribe 'salir' para terminar.")
        while True:
            try:
                user_input = input("Tú: ").strip()
                if user_input.lower() in ['salir', 'exit', 'bye']:
                    print("🤖 ¡Hasta luego!")
                    break

                respuesta = self.buscar_respuesta_semantica(user_input)
                if not respuesta:
                    respuesta = self.generar_respuesta_ia(user_input)

                print(f"🤖 {respuesta}")
                self.log_interaccion(user_input, respuesta)
            except KeyboardInterrupt:
                print("\n🤖 Operación cancelada.")
            except Exception as e:
                print(f"🤖 Error inesperado: {e}")

    def log_interaccion(self, user_input, respuesta):
        with open(self.log_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data.append({"fecha": datetime.now().isoformat(), "usuario": user_input, "respuesta": respuesta})
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    try:
        bot = AdvancedChatbot(json_file="documento.json")
        bot.chat()
    except Exception as e:
        print(f"Error al iniciar el chatbot: {e}")


if __name__ == "__main__":
    main()

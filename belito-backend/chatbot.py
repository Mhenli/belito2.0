import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import fitz
from sentence_transformers import SentenceTransformer, util
import torch
import faiss
import numpy as np

class AdvancedChatbot:
    def __init__(self, pdf_file='documento.pdf', log_file='chatbot_log.json'):
        self.setup_logging(log_file)
        load_dotenv()
        self.text_data = self.load_pdf(pdf_file)  
        self.setup_language_model()
        self.setup_conversation_memory()

        if self.text_data.strip():
            self.setup_semantic_search()  
        else:
            print("⚠️ No se ha cargado texto del PDF.")

    def setup_logging(self, log_file):
        self.log_file = log_file
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def log_interaccion(self, user_input, respuesta):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "respuesta": respuesta
        }
        try:
            with open(self.log_file, 'r+', encoding='utf-8') as f:
                logs = json.load(f)
                logs.append(log_entry)
                f.seek(0)
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Error al registrar log: {e}")

    def load_pdf(self, pdf_file):
        if not os.path.exists(pdf_file):
            print(f"⚠️ El archivo '{pdf_file}' no existe en la ruta especificada.")
            return ""

        try:
            doc = fitz.open(pdf_file)
            print(f"📄 Documento PDF cargado. Páginas: {doc.page_count}")
            text = "\n".join([page.get_text("text") for page in doc])
            if not text.strip():
                print("⚠️ El PDF está vacío o no contiene texto legible.")
            return text
        except Exception as e:
            print(f"⚠️ Error cargando PDF: {e}")
            return ""

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
        if not self.text_data.strip():
            print("⚠️ No hay texto para procesar.")
            return

        print("🔍 Configurando búsqueda semántica...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.modelo = SentenceTransformer("all-MiniLM-L6-v2", device=device)
        
        self.fragmentos_texto = self.dividir_texto(self.text_data)
        print(f"📌 Fragmentos generados: {len(self.fragmentos_texto)}")

        # Obtener embeddings
        self.embeddings_fragmentos = self.modelo.encode(self.fragmentos_texto, convert_to_tensor=True)
        embeddings_np = np.array(self.embeddings_fragmentos.cpu().detach().numpy())

        # Crear un índice FAISS simple con IndexFlatL2 (No es necesario entrenar este índice)
        self.index = faiss.IndexFlatL2(embeddings_np.shape[1])  # FAISS Index Flat L2
        self.index.add(embeddings_np)  # Agregar los embeddings al índice
        print("✅ Índice FAISS configurado para búsqueda semántica.")

    def dividir_texto(self, texto, max_tokens=1200): 
        palabras = texto.split()
        fragmentos = [" ".join(palabras[i:i+max_tokens]) for i in range(0, len(palabras), max_tokens)]
        return fragmentos

    def buscar_respuesta_semantica(self, user_input):
        if not hasattr(self, 'modelo'):
            print("⚠️ El modelo de búsqueda semántica no está inicializado.")
            return None
        
        # Obtener el embedding de la pregunta
        embedding_pregunta = self.modelo.encode(user_input, convert_to_tensor=True)

        # Realizar la búsqueda en el índice FAISS
        similitudes, indices = self.index.search(np.array([embedding_pregunta.cpu().detach().numpy()]), k=1)

        # Obtener el índice y la similitud de la mejor coincidencia
        indice_mejor = indices[0][0]
        max_similitud = similitudes[0][0]

        print(f"🔍 Índice de mejor coincidencia: {indice_mejor} | Similitud: {max_similitud:.4f}")

        # Umbral de similitud ajustado (puedes experimentar con valores más altos)
        if max_similitud < 0.7:  # Aumenta el umbral para asegurarte de que sea relevante
            print("⚠️ La similitud es baja. Intentando con IA para generar respuesta.")
            return None

        fragmento_relevante = self.fragmentos_texto[indice_mejor]
        print(f"✅ Fragmento seleccionado: {fragmento_relevante[:200]}...")

        respuesta_final = self.refinar_respuesta(fragmento_relevante, user_input)
        return respuesta_final

    def refinar_respuesta(self, fragmento, user_input):
        """
        Reformula la respuesta basada en el fragmento seleccionado y la pregunta del usuario.
        """
        prompt = f"""
        Eres Belito, un asistente virtual de Belo. Responde las preguntas de forma clara y amigable, basándote solo en el siguiente fragmento de texto extraído de un PDF. Usa emojis y formato para hacer la respuesta más atractiva y útil.

        Fragmento relevante: 
        {fragmento}

        Pregunta:
        {user_input}

        Respuesta:
        """
        return self.llm(prompt)

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

def main():
    try:
        bot = AdvancedChatbot()
        bot.chat()
    except Exception as e:
        print(f"Error al iniciar el chatbot: {e}")

if __name__ == "__main__":
    main()

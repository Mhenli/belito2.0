"use client";

import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";

interface Message {
  sender: string;
  text: string;
}

const FAQS = [
  "¿Qué es belo?",
  "¿Qué se puede hacer con belo?",
  "¿Cuáles son los beneficios de belo?",
  "¿Dónde se puede usar belo?",
  "¿Cuáles son los requisitos para crear tu cuenta?",
];

// ⬇️ Acá tomamos la variable del .env
const API_URL = process.env.NEXT_PUBLIC_API_URL as string;

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { sender: "🤖 Belito", text: "Hola! Me llamo Belito y estoy acá para ayudarte en lo que necesites, si tenes alguna duda o consulta no dudes en escribirme..." },
  ]);
  const [input, setInput] = useState("");
  const [showFAQs, setShowFAQs] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  const sendMessage = async (message?: string) => {
    const text = message || input;
    if (!text.trim()) return;

    setMessages((prev) => [...prev, { sender: "Tú", text }]);
    setInput("");
    setShowFAQs(false);
    setIsTyping(true);

    try {
      // Usamos la URL del .env
      const { data } = await axios.post(`${API_URL}/chat`, { message: text });

      setTimeout(() => {
        setMessages((prev) => [...prev, { sender: "🤖 Belito", text: data.response }]);
        setIsTyping(false);
      }, 1000); // Simula el tiempo de respuesta del bot
    } catch (error: any) {
      console.error("Error enviando mensaje:", error.response?.data || error.message || error);
      setMessages((prev) => [...prev, { sender: "🤖 Belito", text: "Lo siento, algo salió mal. Intenta nuevamente." }]);
      setIsTyping(false);
  }  
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col items-center justify-center h-screen w-screen bg-white p-4">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg p-10 border-2 flex flex-col h-full">

        {/* Título */}
        <div className="flex items-center justify-center bg-indigo-700 p-2 rounded-md">
          <img
            src="https://assets.belo.app/media/iso-favicom-belo/color/png/app-icon.png"
            alt="Belo Icon"
            className="w-8 h-8 mr-2 rounded-full"
          />
          <h2 className="text-3xl font-bold text-white font-sans">Belito</h2>
        </div>

        {/* Contenedor del chat */}
        <div ref={chatRef} className="flex-1 overflow-y-auto border p-2 my-2 rounded-md">
          {messages.map((msg, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex items-start my-2 ${msg.sender === "Tú" ? "justify-end" : "justify-start"}`}
            >
              {msg.sender !== "Tú" && (
                <img
                  src="https://assets.belo.app/media/iso-favicom-belo/color/png/app-icon.png"
                  alt="Belito"
                  className="w-8 h-8 rounded-full mr-2 self-start"
                />
              )}
              <span
                className={`px-3 py-2 rounded-lg shadow-sm w-fit max-w-[80%] text-sm break-words whitespace-pre-wrap ${
                  msg.sender === "Tú"
                    ? "bg-indigo-700 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                {msg.text}
              </span>
              {msg.sender === "Tú" && (
                <img
                  src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRY-LN3eQJazfKtT_DQnZzOVH2N7MlhlUxWUw&s"
                  alt="Tú"
                  className="w-8 h-8 rounded-full ml-2 self-start"
                />
              )}
            </motion.div>
          ))}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
              className="flex items-center space-x-2 my-2"
            >
              <img
                src="https://assets.belo.app/media/iso-favicom-belo/color/png/app-icon.png"
                alt="Belito"
                className="w-8 h-8 rounded-full"
              />
              <span className="px-3 py-2 rounded-lg shadow-sm w-fit max-w-[80%] text-sm bg-gray-300 text-gray-800">
                <span className="animate-pulse font-extrabold">. . .</span>
              </span>
            </motion.div>
          )}
        </div>

        {/* FAQs */}
        {showFAQs && (
          <div className="mt-2 flex flex-wrap gap-2 justify-center border-t pt-2">
            {FAQS.map((faq, index) => (
              <button
                key={index}
                onClick={() => sendMessage(faq)}
                className="text-white px-3 py-2 bg-indigo-700 rounded text-sm hover:bg-indigo-800 transition"
              >
                {faq}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex items-center mt-2">
          <input
            className="text-black flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-indigo-700"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Chatea conmigo..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button
            onClick={() => sendMessage()}
            className="ml-2 px-4 py-2 bg-indigo-700 text-white rounded hover:bg-indigo-800 transition"
          >
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}

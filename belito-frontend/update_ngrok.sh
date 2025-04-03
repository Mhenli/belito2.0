#!/bin/bash

echo "🌐 Actualizar la URL de ngrok en .env.local"
read -p "👉 Pegá la nueva URL de ngrok (sin / al final): " ngrok_url

echo "NEXT_PUBLIC_API_URL=${ngrok_url}" > .env.local

echo "✅ URL actualizada a ${ngrok_url}"

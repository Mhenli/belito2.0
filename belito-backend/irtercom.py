import requests
import json
import os

# Obtener el token desde la variable de entorno
ACCESS_TOKEN = os.getenv("INTERCOM_ACCESS_TOKEN")

HEADERS = {
    "Intercom-Version": "2.9",
    "accept": "application/json",
    "authorization": f"Bearer {ACCESS_TOKEN}"
}

ARTICLES_URL = "https://api.intercom.io/articles"

def get_articles():
    response = requests.get(ARTICLES_URL, headers=HEADERS)
    
    print(f"\n🔎 Código de respuesta: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])  # Retorna solo los artículos
    else:
        print(f"\n⚠️ Error obteniendo artículos: {response.json()}")
        return []

articles = get_articles()

if articles:
    with open("articles.json", "w", encoding="utf-8") as json_file:
        json.dump(articles, json_file, indent=4, ensure_ascii=False)

    print("\n✅ Artículos guardados en articles.json")
else:
    print("\n⚠️ No se encontraron artículos.")


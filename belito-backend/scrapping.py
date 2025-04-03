import requests
from lxml import html
from urllib.parse import urljoin
import json
import time
import re

BASE_URL = "https://help.belo.app/es/"
data = []

def fetch_page(url):
    """Realiza una solicitud HTTP GET y devuelve el contenido de la página."""
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.content

def extract_collections():
    """Extrae las colecciones de la página principal y devuelve una lista de diccionarios con sus nombres y URLs."""
    content = fetch_page(BASE_URL)
    tree = html.fromstring(content)
    collections = []

    collection_links = tree.xpath('//a[contains(@href, "/es/collections/")]')
    for link in collection_links:
        collection_name = link.text_content().strip()
        collection_url = urljoin(BASE_URL, link.get('href'))
        collections.append({"name": collection_name, "url": collection_url})

    return collections

def extract_breadcrumb(article_tree):
    """Extrae la ruta de navegación y separa en collection y article."""
    xpaths = [
        '//*[@id="main-content"]/section/div/div[2]/div[1]',
        '//*[@id="main-content"]/section/div/div/div[1]'
    ]

    for xpath in xpaths:
        breadcrumb_elements = article_tree.xpath(f"{xpath}//text()")
        breadcrumb_parts = [el.strip() for el in breadcrumb_elements if el.strip()]
        if len(breadcrumb_parts) >= 2:
            return breadcrumb_parts[-2], breadcrumb_parts[-1]  # Collection y Article

    return "Ruta no encontrada", "Ruta no encontrada"

def simple_fetch(url):
    """Obtiene y limpia el contenido HTML de una URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # Limpiar el contenido
        html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content)
        html_content = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', html_content)
        html_content = re.sub(r'<[^>]+>', ' ', html_content)
        html_content = re.sub(r'\s+', ' ', html_content).strip()

        return html_content
    except Exception as e:
        print(f"Error al acceder a la URL: {e}")
        return None

def extract_articles_from_collection(collection):
    """Extrae los artículos dentro de una colección y obtiene la ruta completa y el contenido."""
    content = fetch_page(collection["url"])
    tree = html.fromstring(content)

    article_links = tree.xpath('//a[contains(@href, "/es/articles/")]')
    for link in article_links:
        article_title = link.text_content().strip()
        article_url = urljoin(BASE_URL, link.get('href'))

        # Obtener la ruta de navegación
        article_content = fetch_page(article_url)
        article_tree = html.fromstring(article_content)
        collection_name, article_name = extract_breadcrumb(article_tree)

        # Obtener el contenido limpio
        cleaned_content = simple_fetch(article_url)

        data.append({
            "parent_url": collection["url"],
            "url": article_url,
            "collection": collection_name,
            "article": article_name,
            "content": cleaned_content
        })

        print(f"Extraído: {article_url} -> {collection_name} / {article_name}")
        time.sleep(1)  # Evita sobrecargar el servidor

def main():
    try:
        collections = extract_collections()
        for collection in collections:
            extract_articles_from_collection(collection)

        # Guarda los datos en un archivo JSON
        with open("documento .json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print("✅ Datos guardados en 'belo_help_articles.json'")

    except requests.RequestException as e:
        print(f"Error al realizar la solicitud HTTP: {e}")
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")

if __name__ == "__main__":
    main()

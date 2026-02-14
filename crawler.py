import requests
import os

PAGES_DIR = "pages"
URLS_FILE = "urls.txt"
INDEX_FILE = "index.txt"

os.makedirs(PAGES_DIR, exist_ok=True)

with open(URLS_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

index_lines = []

for i, url in enumerate(urls, start=1):
    try:
        print(f"Downloading {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        filename = f"{i}.html"
        filepath = os.path.join(PAGES_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)

        index_lines.append(f"{i}.html {url}")

    except Exception as e:
        print(f"Error: {url} -> {e}")

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(index_lines))



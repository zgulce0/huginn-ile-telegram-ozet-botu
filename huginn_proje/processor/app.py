import os
import requests
import threading
from flask import Flask, request
from pypdf import PdfReader
from io import BytesIO

app = Flask(__name__)

# Docker-compose içinden gelen token
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
OLLAMA_URL = "OLLAMA_Urlsi"


def process_pdf_background(file_id, chat_id, webhook_url):
    try:
        # 1. Telegram'dan dosya yolunu öğrenelim
        file_info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(file_info_url).json()
        file_path = file_info['result']['file_path']

        # 2. PDF dosyasını indirelim
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        pdf_response = requests.get(download_url)

        # 3. PDF'in içindeki metni çıkaralım
        pdf_file = BytesIO(pdf_response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"

        # Ollama'yı yormamak için metni sınırlayalım (yaklaşık ilk 3-4 sayfa)
        clean_text = text[:8000]

        # 4. Ollama'ya "Şunu özetle" diyelim
        prompt = f"Aşağıdaki metni analiz et ve en önemli yerlerini Türkçe olarak kısa maddelerle özetle:\n\n{clean_text}"

        ollama_payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }

        ollama_res = requests.post(OLLAMA_URL, json=ollama_payload).json()
        summary = ollama_res.get('response', 'Özet çıkarılamadı.')

    except Exception as e:
        summary = f"Hata oluştu: {str(e)}"

    # 5. Sonucu Huginn'e geri fırlatalım
    huginn_payload = {
        "chat_id": chat_id,
        "summary": summary
    }
    requests.post(webhook_url, json=huginn_payload)


@app.route('/process', methods=['POST'])
def process():
    data = request.json
    # Huginn'den gelecek bilgiler
    file_id = data.get('file_id')
    chat_id = data.get('chat_id')
    webhook_url = data.get('webhook_url')

    if not file_id or not webhook_url:
        return "Eksik veri!", 400

    # İşlemi arka planda başlat (Huginn beklemesin diye)
    threading.Thread(target=process_pdf_background, args=(file_id, chat_id, webhook_url)).start()

    return "İşlem sıraya alındı, özet birazdan gelecek.", 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

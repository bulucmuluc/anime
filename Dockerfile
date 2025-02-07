# Python 3.9 tabanlı bir Docker imajı kullan
FROM python:3.9

# Çalışma dizinini belirle
WORKDIR /app

# Gerekli bağımlılıkları yükle (ffmpeg, aria2)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    aria2 \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını kopyala
COPY . .

# Render Web Service için uygun portu belirle
ENV PORT=10000
EXPOSE 10000

# Botu başlat (Render Web Service otomatik olarak bunu çalıştıracak)
CMD ["python3", "bot.py"]

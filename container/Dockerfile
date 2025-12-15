# Immagine Base
FROM python:3.11-slim

# Directory di lavoro
WORKDIR /app

# Dipendenze
COPY requirements.txt .
RUN pip install -r requirements.txt

# Codice Sorgente
COPY . .

# Comando di avvio
CMD ["python", "app.py"]
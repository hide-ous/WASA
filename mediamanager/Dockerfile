# Immagine base Python leggera
FROM python:3.10-slim

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i requisiti e installa le dipendenze
COPY requirements.txt .
# Installazione delle dipendenze: Flask, Mutagen, Watchdog, MusicBrainzNGS
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice sorgente del Media Manager e il frontend
COPY app.py .
COPY index.html .

# Crea le directory di input/output che verranno usate dai volumi, se non già create dal mount
RUN mkdir -p /app/input /app/output

# Il comando di avvio per Flask
CMD ["python", "app.py"]
import redis
from flask import Flask

# Connessione al servizio chiamato "redis"
cache = redis.Redis(host='redis', port=6379)

app = Flask(__name__)


@app.route('/')
def home():
    # Incrementa il contatore nel DB
    count = cache.incr('hits')
    return f"<h1>Questa pagina è stata vista {count} volte.</h1>"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

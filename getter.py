import requests
import json
from ratelimit import limits, sleep_and_retry

# SWAPI: Star Wars API
SWAPI_URL = "https://swapi.dev/api/people/"

CALLS = 1
PERIOD = 3  # Secondi

CHARACTER_ID = 1
NON_EXISTENT_ID = 999



def pretty_print_json(data):
    """
    Stampa l'oggetto Python (derivato da JSON) in un formato indentato e leggibile.
    """
    if data:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print("Nessun dato da visualizzare.")


def print_all_headers(headers):
    """
    Stampa tutte le intestazioni della risposta.
    """
    print("\n--- Intestazioni (Header) Complete ---")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    print("--------------------------------------")


# --- FUNZIONI DI ESECUZIONE HTTP ---

@sleep_and_retry
@limits(calls=CALLS, period=PERIOD)
def execute_network_call(method, url):
    """
    Funzione generica per eseguire una richiesta HTTP (GET o HEAD).

    I decoratori garantiscono che questa funzione aspetti automaticamente (throttling)
    per mantenere il limite di 1 chiamata ogni 1.5 secondi, garantendo stabilità.
    Poiché tutte le funzioni di alto livello (GET, HEAD) chiamano questa funzione,
    il contatore è unico e l'attesa è forzata tra tutte le chiamate.
    """

    if method == 'GET':
        response = requests.get(url)
    elif method == 'HEAD':
        response = requests.head(url)
    else:
        # Questa eccezione non dovrebbe mai essere raggiunta nel contesto di questo script
        raise ValueError("Metodo non supportato in questa funzione.")

    return response


def execute_get_request(url):
    """
    Esegue una richiesta GET per recuperare i dati della risorsa (Metodo SAFE).
    Stampa sempre gli header e il contenuto (JSON formattato) in caso di successo,
    oppure gli header e il tipo di errore in caso di fallimento.

    :param url: L'URL della risorsa.
    :return: I dati JSON deserializzati o None in caso di errore.
    """
    print(f"--- ESECUZIONE GET: {url} ---")

    try:
        response = execute_network_call('GET', url)  # Chiama la funzione rate-limited
    except Exception as e:
        print(f"Errore durante la richiesta: {e}")
        return None

    print(f"Codice di Stato Ricevuto: {response.status_code} ({response.reason})")

    print_all_headers(response.headers)

    if response.status_code == 200:
        try:
            data = response.json()

            print("\n--- Corpo della Risposta (Payload JSON) ---")
            pretty_print_json(data)
            print("-------------------------------------------")

            return data
        except json.JSONDecodeError:
            print("Errore: La risposta non è un JSON valido.")
            return None

    elif response.status_code >= 400:  # Gestisce tutti gli errori 4xx e 5xx
        print(f"ERRORE HTTP: La richiesta ha fallito con lo status code {response.status_code}.")
        return None
    else:
        print(f"Risposta HTTP inattesa: {response.status_code}")
        return None


def execute_head_request(url):
    """Esegue una richiesta HEAD per verificare la risorsa senza scaricare il corpo (Metodo SAFE)."""
    print(f"\n--- ESECUZIONE HEAD: {url} (Solo Header) ---")

    try:
        response = execute_network_call('HEAD', url)  # Chiama la funzione rate-limited
    except Exception as e:
        print(f"Errore durante la richiesta: {e}")
        return

    print(f"Codice di Stato Ricevuto: {response.status_code} ({response.reason})")

    print_all_headers(response.headers)
    if response.status_code >= 400:
        print(f"ERRORE HTTP: La richiesta HEAD ha fallito con lo status code {response.status_code}.")

    # Si noti che il corpo è sempre vuoto per HEAD
    print("\n--- Corpo della Risposta ---")
    print(f"Lunghezza del corpo della risposta HEAD (deve essere 0): {len(response.content)}")
    print("----------------------------")


def main():
    print("ATTIVITÀ WASA: Analisi Pratica dei Metodi HTTP - SOLO METODI SAFE")
    print("--------------------------------------------------")
    print("ASSICURARSI DI AVER INSTALLATO: pip install ratelimit requests")
    print("--------------------------------------------------")

    print("\n[BLOCCO 1] SWAPI: Esplorazione (GET/HEAD, Safe)")
    print("--------------------------------------------------")

    # Esercizio 1.1: GET di successo ($200$ OK)
    # Questa chiamata sarà la prima e non avrà ritardi.
    print("\n======== ESERCIZIO 1.1: GET di successo (Luke Skywalker) - HEADER + BODY ========")
    luke_data = execute_get_request(f"{SWAPI_URL}{CHARACTER_ID}/")

    # Esercizio 1.2: HEAD per efficienza (Solo intestazioni)
    # Questa chiamata *attenderà* 1.5 secondi prima di essere eseguita.
    print("\n======== ESERCIZIO 1.2: HEAD per efficienza - SOLO HEADER ========")
    execute_head_request(f"{SWAPI_URL}{CHARACTER_ID}/")

    # Esercizio 1.3: GET per risorsa inesistente ($404$ Not Found)
    # Questa chiamata *attenderà* 1.5 secondi.
    print("\n======== ESERCIZIO 1.3: GET per risorsa inesistente (404) - HEADER + BODY ========")
    execute_get_request(f"{SWAPI_URL}{NON_EXISTENT_ID}/")

    # Esercizio 1.4: Navigazione (Hypermedia)
    if luke_data and 'homeworld' in luke_data:
        homeworld_url = luke_data['homeworld']
        print("\n======== ESERCIZIO 1.4: Seguire il Link 'homeworld' (Navigazione) - HEADER + BODY ========")
        print(f"Recupero dati da: {homeworld_url}")
        # Questa chiamata *attenderà* 1.5 secondi.
        # Stampa il JSON completo formattato per l'analisi del pianeta
        execute_get_request(homeworld_url)


if __name__ == "__main__":
    main()

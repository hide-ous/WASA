import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# In Python, l'oggetto 'Future' (spesso combinato con 'async/await')
# è l'equivalente concettuale più vicino a una Promise di JavaScript.

def operazione_lenta(numero):
    """Funzione che simula un'operazione che richiede tempo (ad esempio, I/O o un calcolo pesante)."""
    print(f"  [Task] Inizio operazione per il numero {numero}...")
    time.sleep(2)  # Simula un ritardo di 2 secondi
    risultato = numero * numero
    print(f"  [Task] Operazione completata. Risultato: {risultato}")
    return risultato


async def gestore_principale():
    """Funzione async principale che utilizza un Future."""
    print("Programma avviato.")

    # 1. Creiamo un Executor per eseguire l'operazione lenta in un thread separato.
    # Questo mantiene il main thread (o l'Event Loop) libero.
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()

    # 2. Creiamo un Future. Questo è l'oggetto "segnaposto" (come la Promise)
    # per il risultato futuro.
    # `loop.run_in_executor` restituisce un oggetto Future.
    future = loop.run_in_executor(executor, operazione_lenta, 5)

    print("Il codice continua ad eseguire immediatamente, non bloccato dal Future...")
    print(f"Stato del Future: {future._state}")

    # 3. Aspettiamo (await) il completamento del Future.
    # Questo è l'equivalente di .then() e attende il risultato.
    try:
        # L'esecuzione si ferma qui finché l'operazione_lenta non restituisce il suo valore.
        risultato_promise = await future
        print(f"\n[Successo - .then()] Risultato ricevuto dal Future: {risultato_promise}")

    except Exception as e:
        # Questo è l'equivalente di .catch()
        print(f"\n[Errore - .catch()] Si è verificato un errore: {e}")

    finally:
        executor.shutdown()
        print("Programma terminato.")


# Eseguiamo la funzione asincrona principale.
if __name__ == "__main__":
    asyncio.run(gestore_principale())
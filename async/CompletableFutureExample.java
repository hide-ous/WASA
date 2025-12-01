import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

// In Java, CompletableFuture è il meccanismo idiomatico per gestire risultati
// asincroni e incatenare operazioni in modo non bloccante,
// ed è l'equivalente più diretto di una Promise.

public class CompletableFutureExample {

    // Funzione che simula un'operazione asincrona
    public static CompletableFuture<String> recuperaDatiUtente(int userId) {
        // L'ExecutorService gestisce l'esecuzione del codice in un thread separato.
        ExecutorService executor = Executors.newSingleThreadExecutor();

        return CompletableFuture.supplyAsync(() -> {
            try {
                System.out.println("  [Task] Ricerca utente " + userId + " avviata su thread: " + Thread.currentThread().getName());
                TimeUnit.SECONDS.sleep(1); // Simula un ritardo di I/O

                if (userId == 404) {
                    // Questa eccezione viene "catturata" dal blocco .exceptionally()
                    throw new RuntimeException("Utente non trovato! (ID: " + userId + ")");
                }

                return "Dati Utente per ID: " + userId;
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException(e);
            } finally {
                // In un'applicazione reale, l'executor non verrebbe spento qui,
                // ma riutilizzato. Lo spengiamo per questo esempio di console.
                executor.shutdown();
            }
        });
    }

    public static void main(String[] args) {
        System.out.println("Programma avviato.");

        // 1. Chiamata Asincrona (Restituisce un CompletableFuture<String>)
        CompletableFuture<String> datiUtenteCF = recuperaDatiUtente(101);

        System.out.println("Il codice principale continua ad eseguire immediatamente, in attesa della CompletableFuture...");

        // 2. Chaining e Gestione del Risultato (.then() e .thenApply())
        // La catena termina con thenAccept, quindi il risultato è CompletableFuture<Void>.
        CompletableFuture<Void> datiPromiseChain = datiUtenteCF
            // .thenApply: Esegue una trasformazione sul risultato, restituendo una nuova String.
            .thenApply(dati -> {
                System.out.println("\n[Successo - thenApply] Trasformazione dati in corso: " + dati);
                return "Elaborato: " + dati.toUpperCase();
            })
            // .exceptionally: Gestisce gli errori, restituendo un valore di fallback String
            .exceptionally(eccezione -> {
                System.err.println("\n[Errore - exceptionally] Eccezione catturata: " + eccezione.getMessage());
                return "Risultato di default (fallback) in caso di errore"; // Ritorna String
            })
            // .thenAccept: Esegue un'azione sul risultato finale (ritorna CompletableFuture<Void>).
            .thenAccept(risultatoFinale -> {
                System.out.println("[Successo - thenAccept] Risultato finale gestito: " + risultatoFinale);
            });

        // Esempio di gestione di un errore (ID 404). Anche questa catena finisce in Void.
        CompletableFuture<Void> errorePromiseChain = recuperaDatiUtente(404)
            // .exceptionally deve restituire una String.
            .exceptionally(eccezione -> {
                System.err.println("\n[Errore - exceptionally] Gestione errore 404: " + eccezione.getMessage());
                return "Messaggio di fallback per ID 404";
            })
            // .thenAccept termina la catena.
            .thenAccept(msg -> {
                System.out.println("[Successo - thenAccept] Messaggio elaborato dopo fallback: " + msg);
            });


        // Per le applicazioni console, è necessario attendere esplicitamente che i thread
        // asincroni terminino. Ora facciamo join() sulle catene CompletableFuture<Void>.
        try {
            // Blocca fino al completamento delle catene di CompletableFuture.
            datiPromiseChain.join();
            errorePromiseChain.join();
        } catch (Exception e) {
            System.err.println("Errore durante l'attesa del completamento: " + e.getMessage());
        }

        System.out.println("\nProgramma terminato.");
    }
}
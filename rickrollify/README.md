### Consegna
- **Base**: Modifica `rickrollify.js` usando `document.querySelectorAll('a')` per trovare tutti gli elementi link e modificare il loro attributo href.
- **Avanzata**: Introduci uno switch all'interno di `popup.html` che permetta di abilitare/disabilitare la funzionalità.

---
## istruzioni per sviluppare ed installare l'estensione
1. Crea una nuova cartella vuota chiamata Rickrollify. Inseriscici i file di questa cartella.

2. File Manifest (`manifest.json`)
Il manifest.json indica a Chrome il nome, la versione, le icone e, soprattutto, a quali file e permessi ha bisogno di accedere.
   - action: Definisce cosa succede quando l'utente clicca sull'icona dell'estensione (mostra popup.html).
   - content_scripts: Dice a Chrome di iniettare ed eseguire lo script rickrollify.js su tutte le pagine (`<all_urls>`).

3. Script di Rickroll (`rickrollify.js`)
Questo è lo script JavaScript che effettuerà la vera e propria modifica del DOM. 
4. Pagina di Pop-up (`popup.html`)
Questa è una semplice interfaccia utente che viene visualizzata quando l'utente fa clic sull'icona dell'estensione. 

5. Installazione su Chrome 
   1. Apri Chrome e vai su `chrome://extensions`.
   2. Assicurati che l'interruttore "Modalità sviluppatore" (Developer mode) sia attivato
   3. Carica estensione non pacchettizzata
   4. Seleziona la cartella Rickrollify che hai appena creato.
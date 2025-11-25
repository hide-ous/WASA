// da applicare a
// https://corsidilaurea.uniroma1.it/it/course/33503/attendance/lessons-plan
/**
 * Script per l'estrazione dettagliata dei corsi (Insegnamento, Anno, Semestre, CFU)
 * direttamente dalla tabella del piano di studi utilizzando le API del DOM.
 *
 * I risultati vengono strutturati in un array di oggetti JSON.
 */
function extractCourseDetails() {
    console.log('--- Inizio Estrazione Dettagli Tabella Corsi ---');

    // 1. Trova tutte le righe dei corsi (<tr>) con la classe 'activity'.
    // Questa selezione ignora le righe di intestazione e raggruppamento non necessarie.
    const courseRows = document.querySelectorAll('tr.activity');

    if (courseRows.length === 0) {
        console.error("ERRORE JS: Nessuna riga di corso trovata (selettore: 'tr.activity').");
        return [];
    }

    let structuredData = [];

    // 2. Itera su ciascuna riga del corso
    courseRows.forEach((row, index) => {
        // Se si tratta di un modulo figlio, saltalo per evitare duplicazioni,
        // dato che i dati di Anno/Semestre/CFU sono già presenti nella riga padre,
        // a meno che tu non voglia i dettagli specifici del modulo.
        if (row.classList.contains('child')) {
            // Esempio: "I MODULO" o "II MODULO"
            // Se si vuole includere solo il modulo (come riga separata),
            // si può commentare l'if e usare il codice sottostante.
            // Per ora, lo saltiamo per concentrarci sui corsi principali.
            // Se volessi includerli, l'attività padre viene identificata dal campo data-parent-id
            return;
        }

        // Seleziona tutte le celle (<td>) all'interno della riga
        const cells = row.querySelectorAll('td');

        if (cells.length < 4) {
            console.warn(`Riga ${index + 1} incompleta. Saltata.`);
            return;
        }

        // 3. Estrai i dati dalla prima cella (TD[0])
        const firstCell = cells[0];

        // Estrai il nome dell'attività (l'elemento con la classe activity-name)
        const activityNameElement = firstCell.querySelector('.activity-name');
        const activityName = activityNameElement ? activityNameElement.textContent.trim() : 'N/D';

        // Estrai il codice SSD e la Lingua (l'elemento <strong>)
        const metadataElement = firstCell.querySelector('strong.text-nowrap');
        let ssd = 'N/D';
        let language = 'N/D';

        if (metadataElement) {
            const text = metadataElement.textContent.trim().replace(/[\[\]]/g, ''); // Rimuove parentesi quadre
            const parts = text.split(' ');
            if (parts.length >= 2) {
                ssd = parts[0];
                language = parts[1];
            }
        }

        // Estrai il codice dell'attività (opzionale, se presente)
        const activityCodeElement = firstCell.querySelector('.activity-code');
        const activityCode = activityCodeElement ? activityCodeElement.textContent.trim() : 'N/D';


        // 4. Estrai i dati dalle celle successive (TD[1], TD[2], TD[3])

        // 5. Costruisci l'oggetto dati
        structuredData.push({
            code: activityCode,
            name: activityName,
            ssd: ssd,
            language: language,
            // year: year,
            // semester: semester,
            // cfu: isNaN(cfu) ? 0 : cfu
        });
    });

    // 6. Visualizza il risultato finale
    console.log('\n==================================================================');
    console.log(`Estrai ${structuredData.length} corsi principali dalla tabella:`);
    console.table(structuredData);
    console.log('==================================================================');

    return structuredData;
}

// Esegui la funzione e mostra il risultato
const extractedCoursesDetails = extractCourseDetails();
// L'array di oggetti è ora disponibile nella console come 'extractedCoursesDetails'
console.log('Variabile Array di oggetti JSON con i dettagli dei corsi:');
extractedCoursesDetails;
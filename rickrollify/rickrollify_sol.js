const RICKROLL_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

/**
 * Funzione principale per trovare e modificare tutti i link nella pagina.
 */
function rickrollifyLinks() {
    const links = document.querySelectorAll('a');
    let modifiedCount = 0;

    links.forEach(link => {
        const originalHref = link.getAttribute('href');

        // Assicurati che l'elemento sia effettivamente un link e non un anchor vuoto
        if (originalHref && originalHref.trim() !== '' && !originalHref.startsWith('#')) {
            link.setAttribute('href', RICKROLL_URL);
            link.removeAttribute('target');

            modifiedCount++;
        }
    });

    console.log(`[Rickrollify] Modificati con successo ${modifiedCount} link con l'URL di Rickroll.`);
}

// Esegui la funzione non appena lo script viene caricato dalla pagina
rickrollifyLinks();
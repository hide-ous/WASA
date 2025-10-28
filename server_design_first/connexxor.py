import connexion

# 1. Inizializza l'applicazione Connexion (usando Uvicorn come base)
app = connexion.App(__name__, specification_dir='.')

# 2. Carica la specifica OpenAPI
# base_path='/api' definisce il prefisso per tutte le rotte.
app.add_api(
    'poketeam_full.yaml',
    base_path='/api',
    strict_validation=True,
    validate_responses=True # Valida anche la risposta prodotta dalla funzione Python!
)

if __name__ == '__main__':
    # 3. Avvia il server
    print("Server Connexion avviato. Endpoint disponibili definiti in team_builder_api.yaml")
    print("POST /api/teams")
    app.run(port=8080)



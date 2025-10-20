# Simula un database in memoria per semplicità
TEAMS_DATABASE = {}
NEXT_TEAM_ID = 1


def create_team(body):
    """
    Implementa l'operazione 'create_team' definita nell'OpenAPI YAML.

    Connexion si occupa di:
    1. Validare il 'body' della richiesta contro lo schema 'NewTeamRequest'.
       Se la validazione fallisce (es. 'name' mancante), la funzione non viene nemmeno chiamata
       e Connexion restituisce automaticamente un errore 400.
    2. Passare il corpo deserializzato della richiesta come un dizionario Python (body).
    """
    global NEXT_TEAM_ID

    # 1. Estrai i dati validati da Connexion
    team_name = body.get('name')
    trainer_name = body.get('trainer')
    pokemon_names = body.get('pokemon_names', [])

    # 2. Logica di Business
    if len(pokemon_names) > 6:
        # Anche se c'è 'maxItems: 6' nello schema, aggiungiamo una verifica esplicita
        # per logiche più complesse che non possono essere coperte solo dallo schema.
        # Connexion gestisce già la maggior parte degli errori di validazione dello schema.
        return {"error": "Un team non può avere più di 6 Pokémon."}, 400

    team_id = NEXT_TEAM_ID

    # 3. Salva i dati simulati nel "database"
    new_team = {
        "id": team_id,
        "name": team_name,
        "trainer": trainer_name,
        "pokemon_names": pokemon_names,
        "members_count": len(pokemon_names)
    }

    TEAMS_DATABASE[team_id] = new_team
    NEXT_TEAM_ID += 1

    # 4. Prepara la risposta (Connexion serializza questo dict in JSON e
    #    lo valida contro lo schema 'Team' definito per il 201)
    response_data = {
        "id": new_team["id"],
        "name": new_team["name"],
        "trainer": new_team["trainer"],
        "members_count": new_team["members_count"]
    }

    # Restituisci l'oggetto e il codice di stato HTTP
    return response_data, 201

# Aggiungi qui altre funzioni come get_team_by_id, update_team, ecc.

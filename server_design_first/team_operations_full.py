import requests
from http import HTTPStatus
from typing import Dict, Any, Tuple, List

# ----------------------------------------------------------------------
# Configurazione e "Database" simulato (In-Memory)
# ----------------------------------------------------------------------
# Simula un database in memoria per semplicità. Ho cambiato i nomi
# delle variabili per allinearli al codice fornito.
TEAMS_DATABASE: Dict[int, Dict[str, Any]] = {}
NEXT_TEAM_ID = 1
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"


# ----------------------------------------------------------------------
# Funzione Helper: Arricchimento dei dati dei Pokémon (Sincrona/Bloccante)
# ----------------------------------------------------------------------
def _get_pokemon_details_sync(pokemon_name: str) -> Dict[str, Any]:
    """
    Recupera i dettagli di un singolo Pokémon da PokéAPI (Sincrona/Bloccante).
    Questa è la parte che blocca il thread in Connexion/Uvicorn.
    """
    # Connexion dovrebbe passare l'ID come stringa, ma il nostro database usa int.
    name_lower = pokemon_name.lower().strip()

    try:
        # Chiamata di rete sincrona e bloccante
        response = requests.get(f"{POKEAPI_BASE_URL}{name_lower}", timeout=5)

        if response.status_code == HTTPStatus.NOT_FOUND:
            # Dettagli in caso il Pokémon non esista (simulazione FullTeamResponse)
            return {
                "name": pokemon_name,
                "types": ["Sconosciuto"],
                "abilities": ["Non trovato in PokéAPI"]
            }

        response.raise_for_status()
        data = response.json()
        print('got from pokeapi:')
        print(data)

        # Struttura dati come definita in FullTeamResponse -> PokemonDetail
        details = {
            "name": data['name'].capitalize(),
            "types": [t['type']['name'].capitalize() for t in data['types']],
            "abilities": [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
        }
        return details

    except requests.exceptions.RequestException as e:
        print(f"ERRORE DI CONNESSIONE/API ESTERNA per {pokemon_name}: {e}")
        return {
            "name": pokemon_name,
            "types": ["Errore API"],
            "abilities": ["Dati esterni non disponibili"]
        }


# ----------------------------------------------------------------------
# Endpoint: POST /teams
# ----------------------------------------------------------------------
def create_team(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Implementa l'operazione 'create_team'.
    Nota: ho rinominato l'argomento in 'body' per allinearmi al tuo snippet.
    """
    global NEXT_TEAM_ID

    # 1. Estrai i dati validati da Connexion
    team_name = body.get('name')
    trainer_name = body.get('trainer')
    pokemon_names = body.get('pokemon_names', [])

    # 2. Logica di Business
    if len(pokemon_names) > 6:
        return {"error": "Un team non può avere più di 6 Pokémon."}, HTTPStatus.BAD_REQUEST

    team_id = NEXT_TEAM_ID

    # 3. Salva i dati simulati nel "database"
    new_team = {
        "id": team_id,
        "name": team_name,
        "trainer": trainer_name,
        "pokemon_names": pokemon_names,
    }

    TEAMS_DATABASE[team_id] = new_team
    NEXT_TEAM_ID += 1

    # 4. Prepara la risposta (TeamResponse)
    response_data = {
        "id": new_team["id"],
        "name": new_team["name"],
        "trainer": new_team["trainer"],
        "pokemon_names": new_team["pokemon_names"],
    }

    # Restituisci l'oggetto e il codice di stato HTTP
    return response_data, HTTPStatus.CREATED


# ----------------------------------------------------------------------
# Endpoint: GET /teams/{team_id}
# ----------------------------------------------------------------------
def get_team_by_id(team_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Implementa l'operazione 'get_team_by_id'.
    Recupera un team e arricchisce i dati dei Pokémon da PokéAPI.

    :param team_id: L'ID del Team da recuperare, passato dal path.
    :return: Una tupla con (dati del Team, codice di stato HTTP).
    """
    try:
        # Connexion passa team_id come stringa (anche se era un path int).
        # Lo convertiamo in int per cercare nel nostro database simulato.
        team_id_int = int(team_id)
    except ValueError:
        # Se l'ID non è un numero valido, lo consideriamo come non trovato o malformato
        return {"error": "Invalid Team ID format."}, HTTPStatus.BAD_REQUEST

    team = TEAMS_DATABASE.get(team_id_int)

    if not team:
        # Gestisce il 404 come richiesto dallo schema OpenAPI
        return {"error": "Team Not Found"}, HTTPStatus.NOT_FOUND

    enriched_team = team.copy()

    detailed_pokemon: List[Dict[str, Any]] = []

    # 1. Recupera i dettagli arricchiti per ciascun Pokémon
    # NOTA: Queste sono le chiamate di rete bloccanti!
    for name in team.get('pokemon_names', []):
        details = _get_pokemon_details_sync(name)
        print(details)
        detailed_pokemon.append(details)

    # 2. Struttura l'oggetto FullTeamResponse
    enriched_team['id'] = enriched_team['id']  # Conversione ID a stringa
    enriched_team['pokemon_details'] = detailed_pokemon

    # Rimuoviamo la chiave 'id' che era int e ne lasciamo solo una string
    # Rimuoviamo la chiave 'members_count' aggiunta nella create_team
    if 'members_count' in enriched_team:
        del enriched_team['members_count']

    # 3. Restituisci l'oggetto FullTeamResponse e il codice HTTP 200
    return enriched_team, HTTPStatus.OK

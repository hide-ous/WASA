import os
from itertools import islice

import requests
import json

from http_utils import download

CHROME_UA = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.166 Safari/537.36"

API_BASE_URL = 'https://pokeapi.co/api/v2'
POKEMON_ENDPOINT = f'{API_BASE_URL}/pokemon/'

POKEMON_SEARCH_PARAMS = '?limit=100000&offset=0'

CRY_SAVE_PATH = 'cries'
POKE_DETAILS_SAVE_PATH = 'pokemons.jsonl'
if __name__ == '__main__':
    os.makedirs(CRY_SAVE_PATH, exist_ok=True)

    search_query = POKEMON_ENDPOINT + POKEMON_SEARCH_PARAMS
    print(f'asking for all pokemons: {search_query}')
    all_pokemons = json.loads(requests.get(search_query, headers={'User-Agent':
                                                                      CHROME_UA}).content)
    print(f'got {all_pokemons["count"]} pokemons')

    with open(POKE_DETAILS_SAVE_PATH, 'w') as f:
        for i, pokemon in enumerate(islice(all_pokemons['results'], 20)):
            print(f'{i}. found {pokemon["name"]}: getting details from {pokemon["url"]}')
            pokemon_detail = json.loads(requests.get(pokemon['url']).content)
            f.write(json.dumps(pokemon_detail) + '\n')
            for cry_key, cry in pokemon_detail.get('cries', dict()).items():
                download(cry, f"{CRY_SAVE_PATH}/{cry_key}_{cry.split('/')[-1]}")

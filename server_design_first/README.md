## Esecuzione
1. Assicurati di avere i moduli: `pip install connexion[uvicorn,swagger-ui]`
2. Esegui: `python connexxor.py`
3. La documentazione API è disponibile all'indirizzo http://127.0.0.1:8080/api/ui
3. Testa con i seguenti comandi:
   - Windows 
     ```cmd
     curl -X POST http://127.0.0.1:8080/api/teams -H "Content-Type: application/json" -d "{\"name\":\"Team Elettro\",\"trainer\":\"Lt. Surge\",\"pokemon_names\":[\"Raichu\",\"Electabuzz\"]}"
     ```
   - *nix: 
    ```shell
         curl -X POST http://127.0.0.1:8080/api/teams \
         -H "Content-Type: application/json" \
         -d '{
             "name": "Team Blaze",
             "trainer": "Giovanni",
             "pokemon_names": ["Charizard", "Arcanine", "Ninetales"]
         }'
    ```
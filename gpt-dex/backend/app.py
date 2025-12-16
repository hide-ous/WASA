from flask import Flask, jsonify
import requests

app = Flask(__name__)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


@app.route("/pokemon/<int:pokedex_id>", methods=["GET"])
def get_pokemon_stats(pokedex_id):
    """
    Fetch basic stats for a Pokémon given its Pokédex ID.
    """
    url = f"{POKEAPI_BASE_URL}/{pokedex_id}"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({
            "error": "Pokemon not found",
            "pokedex_id": pokedex_id
        }), 404

    data = response.json()

    # Extract types
    types = [t["type"]["name"] for t in data["types"]]

    # Extract base stats
    stats = {
        stat["stat"]["name"]: stat["base_stat"]
        for stat in data["stats"]
    }

    result = {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "types": types,
        "stats": {
            "hp": stats.get("hp"),
            "attack": stats.get("attack"),
            "defense": stats.get("defense"),
            "special-attack": stats.get("special-attack"),
            "special-defense": stats.get("special-defense"),
            "speed": stats.get("speed")
        }
    }

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

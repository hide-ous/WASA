import json
import sqlite3
import requests
from flask import Flask, jsonify

app = Flask(__name__)

DB_PATH = "/data/pokemon.db"
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with open("/app/db/init.sql", "r") as f:
        sql = f.read()
    conn = get_db()
    conn.executescript(sql)
    conn.close()


init_db()


@app.route("/pokemon/<int:pokedex_id>", methods=["GET"])
def get_pokemon(pokedex_id):
    conn = get_db()
    cur = conn.cursor()

    # 1️⃣ check cache
    cur.execute(
        "SELECT name, height, weight, types, stats FROM pokemon WHERE id = ?",
        (pokedex_id,)
    )
    row = cur.fetchone()

    if row:
        conn.close()
        return jsonify({
            "id": pokedex_id,
            "name": row[0],
            "height": row[1],
            "weight": row[2],
            "types": json.loads(row[3]),
            "stats": json.loads(row[4]),
            "source": "cache"
        })

    # 2️⃣ fetch from PokeAPI
    response = requests.get(f"{POKEAPI_BASE_URL}/{pokedex_id}")
    if response.status_code != 200:
        conn.close()
        return jsonify({"error": "Pokemon not found"}), 404

    data = response.json()

    types = [t["type"]["name"] for t in data["types"]]
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    # 3️⃣ save to cache
    cur.execute(
        """
        INSERT INTO pokemon (id, name, height, weight, types, stats)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["id"],
            data["name"],
            data["height"],
            data["weight"],
            json.dumps(types),
            json.dumps(stats)
        )
    )
    conn.commit()
    conn.close()

    return jsonify({
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "types": types,
        "stats": stats,
        "source": "pokeapi"
    })



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

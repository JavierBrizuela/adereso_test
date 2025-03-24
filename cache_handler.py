import os
import json
import requests
   
def fetch_pokemon_names():
    if not os.path.exists("pokemon.json"):
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1400")
        result = [p["name"] for p in response.json()["results"]]
        with open("pokemon.json", "w") as f:
            json.dump(result, f, indent=2)
        return result
    else:
        with open("pokemon.json", "r") as f:
            return json.load(f) 

def fetch_sw_characters():
    if not os.path.exists("starwar_characters.json"):
        base_url = "https://swapi.dev/api/people/"
        characters = []
    
        while base_url:
            response = requests.get(base_url)
            data = response.json()
            characters.extend([format_character_name(p["name"]) for p in data["results"]])
            base_url = data["next"]  # URL de la siguiente página (ej: "https://swapi.dev/api/people/?page=2")
        
        with open("starwar_characters.json", "w") as f:
            json.dump(characters, f, indent=2)
        return characters
        
    else:
        with open("starwar_characters.json", "r") as f:
            return json.load(f) 
    
def fetch_sw_planets():
    if not os.path.exists("starwar_planets.json"):
        base_url = "https://swapi.dev/api/planets/"
        planets = []
    
        while base_url:
            response = requests.get(base_url)
            data = response.json()
            planets.extend([format_character_name(p["name"]) for p in data["results"]])
            base_url = data["next"]  # URL de la siguiente página (ej: "https://swapi.dev/api/people/?page=2")
        
        with open("starwar_planets.json", "w") as f:
            json.dump(planets, f, indent=2)
        return planets
        
    else:
        with open("starwar_planets.json", "r") as f:
            return json.load(f) 

def load_cache(cache_file):
    """Cargar caché desde archivo JSON."""
    if not os.path.exists(cache_file):
        return {
            "Pokemon": {},
            "StarWarsCharacter": {},
            "StarWarsPlanet": {}
        }
    try:
        with open(cache_file, "r") as f:
            return json.load(f)
    except:
        return {"Pokemon": {}, "StarWarsCharacter": {}, "StarWarsPlanet": {}}

def save_cache(cache_file, cache):
    """Guardar caché en archivo (ejecutar periódicamente)."""
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)
        
def format_character_name(name):
    # Ejemplo de formato: convertir a minúsculas y reemplazar espacios con guiones bajos
    return name.lower().replace(" ", "_")
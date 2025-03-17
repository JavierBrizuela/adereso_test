import requests
import re
import os
import json
import time
from difflib import get_close_matches
from datetime import datetime, timedelta

class ChallengeSolver:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.cache_file = "api_cache.json"
        self.cache = self.load_cache()
        self.pokemon_names = self.fetch_pokemon_names()
        self.star_wars_characters = self.fetch_sw_characters()
        self.star_wars_planets = self.fetch_sw_planets()
        self.start_time = None
        self.time_limit = 180  # 3 minutos en segundos            

    def fetch_pokemon_names(self):
        if not os.path.exists("pokemon.json"):
            response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1400")
            result = [p["name"] for p in response.json()["results"]]
            with open("pokemon.json", "w") as f:
                json.dump(result, f, indent=2)
            return result
        else:
            with open("pokemon.json", "r") as f:
                return json.load(f) 

    def fetch_sw_characters(self):
        if not os.path.exists("starwar_characters.json"):
            base_url = "https://swapi.dev/api/people/"
            characters = []
        
            while base_url:
                response = requests.get(base_url)
                data = response.json()
                characters.extend([self.format_character_name(p["name"]) for p in data["results"]])
                base_url = data["next"]  # URL de la siguiente página (ej: "https://swapi.dev/api/people/?page=2")
            
            with open("starwar_characters.json", "w") as f:
                json.dump(characters, f, indent=2)
            return characters
            
        else:
            with open("starwar_characters.json", "r") as f:
                return json.load(f) 
        
    def fetch_sw_planets(self):
        if not os.path.exists("starwar_planets.json"):
            base_url = "https://swapi.dev/api/planets/"
            planets = []
        
            while base_url:
                response = requests.get(base_url)
                data = response.json()
                planets.extend([self.format_character_name(p["name"]) for p in data["results"]])
                base_url = data["next"]  # URL de la siguiente página (ej: "https://swapi.dev/api/people/?page=2")
            
            with open("starwar_planets.json", "w") as f:
                json.dump(planets, f, indent=2)
            return planets
            
        else:
            with open("starwar_planets.json", "r") as f:
                return json.load(f) 
    
    def load_cache(self):
        """Cargar caché desde archivo JSON."""
        if not os.path.exists(self.cache_file):
            return {
                "Pokemon": {},
                "StarWarsCharacter": {},
                "StarWarsPlanet": {}
            }
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except:
            return {"Pokemon": {}, "StarWarsCharacter": {}, "StarWarsPlanet": {}}
    
    def save_cache(self):
        """Guardar caché en archivo (ejecutar periódicamente)."""
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)
    
    def format_character_name(self, name):
        # Ejemplo de formato: convertir a minúsculas y reemplazar espacios con guiones bajos
        return name.lower().replace(" ", "_")
        
    def correct_entity_name(self, name, entity_type):
        if entity_type == "Pokemon":
            valid_names = self.pokemon_names
        elif entity_type == "StarWarsCharacter":
            valid_names = self.star_wars_characters
        elif entity_type == "StarWarsPlanet":
            valid_names = self.star_wars_planets
        else:
            return name

        corrected = get_close_matches(name, valid_names, n=1, cutoff=0.7)
        return corrected[0] if corrected else name
    
    def validate_entity_type(self, entity_name, parsed_entity_type):
        # Verificar si el nombre existe en el tipo propuesto
        if parsed_entity_type == "Pokemon" and entity_name in self.pokemon_names:
            return parsed_entity_type
        elif parsed_entity_type == "StarWarsCharacter" and entity_name in self.star_wars_characters:
            return parsed_entity_type
        elif parsed_entity_type == "StarWarsPlanet" and entity_name in self.star_wars_planets:
            return parsed_entity_type
        
        # Si no coincide, detectar el tipo real
        if entity_name in self.pokemon_names:
            return "Pokemon"
        elif entity_name in self.star_wars_characters:
            return "StarWarsCharacter"
        elif entity_name in self.star_wars_planets:
            return "StarWarsPlanet"
        
        return parsed_entity_type  # Conservar el original si no se encuentra

    def get_expression_from_ai(self, problem_text):
        chat_url = "https://recruiting.adere.so/chat_completion"
        messages = [
                    {
                        "role": "system",
                        "content": 
                        """
                        ### Instrucciones Estrictas:
                        1. **NO omitas ningún término** del enunciado, incluso si crees que un atributo no existe.
                        2. **Sigue el formato** `[TipoEntidad:nombre_entidad.atributo]` para todos los elementos.
                        3. **Usa solo estos atributos válidos**:
                        - StarWarsPlanet: surface_water, rotation_period, population, diameter, orbital_period
                        - StarWarsCharacter: height, mass, homeworld
                        - Pokemon: base_experience, height, weight
                        4. **PROPORCIONA SOLO UNA EXPRESIÓN MATEMÁTICA FINAL** que resuelva todo el problema de una vez.
                        5. **ENVUELVE LA EXPRESIÓN FINAL** entre triple backtick + math, UNA SOLA VEZ al final:
                        ```math
                        (StarWarsPlanet:tatooine.population * Pokemon:pikachu.height)
                        ```

                        **Formato Estricto**:
                        - Usar `[TipoEntidad:nombre.atributo]`.
                        - Operadores: `+`, `-`, `*`, `/`.
                        - NO USES MÚLTIPLES BLOQUES DE CÓDIGO MATH, solo UNO FINAL con la expresión completa.

                        **IMPORTANTE PARA DIVISIONES**:
                        - Para expresiones del tipo "cuántas veces X cabe en Y", la fórmula SIEMPRE debe ser `Y / X`.
                        - El dividendo (numerador) debe ser lo que contiene, y el divisor (denominador) debe ser lo que cabe.

                        **IMPORTANTE PARA RESTAS**:
                        - Si el problema dice "X resta su valor del valor de Y", la fórmula SIEMPRE debe ser `Y - X`.
                        - Si el problema dice "restar X de Y", la fórmula SIEMPRE debe ser `Y - X`.

                        **Ejemplos de respuestas correctas**:
                        - Para un problema que requiera sumar dos divisiones:
                        NO HAGAS:
                        ```math
                        División1
                        ```
                        ```math
                        División2
                        ```
                        ```math
                        División1 + División2
                        ```
                        
                        CORRECTO:
                        ```math
                        (División1) + (División2)
                        ```

                        - Problema: "Calcular cuántas veces el peso de Cradily cabe en el periodo de rotación de Rodia y luego sumar cuántas veces la altura de R2-D2 cabe en la altura del Conde Dooku"
                        RESPUESTA CORRECTA:
                        ```math
                        (StarWarsPlanet:rodia.rotation_period / Pokemon:cradily.weight) + (StarWarsCharacter:dooku.height / StarWarsCharacter:r2d2.height)
                        ```
                        """
                    },
                    {"role": "user", "content": problem_text}
                ]
        
        payload = {"model": "gpt-4o-mini", "messages": messages}
        response = requests.post(chat_url, headers=self.headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    
    def extract_expression(self, text):
        # Buscar todos los patrones ```math [expresión] ```
        matches = re.findall(r'```math\n(.*?)\n```', text, re.DOTALL)
        if not matches:
            return None
        # Tomar la última expresión (que debería ser la final completa)
        final_expression = matches[-1].strip()
        # Eliminar cualquier comentario o texto extra
        final_expression = re.sub(r'#.*$', '', final_expression).strip()
        
        return final_expression
    
    def parse_term(self, term):
        try:
            type_part, rest = term.split(':', 1)
            name, attrs = rest.split('.', 1)
            original_name = name
            print(f"type: {type_part} - name: {name} - attrs: {attrs}")
            # Primera corrección de nombre
            name = self.correct_entity_name(name, type_part)
            # Validación cruzada de tipo
            validated_type = self.validate_entity_type(name, type_part)
            
            # Si el tipo cambió, volver a corregir el nombre con el tipo validado
            if validated_type != type_part:
                name = self.correct_entity_name(original_name, validated_type)
            return {
                'type': type_part,
                'name': name,
                'attribute_path': attrs if attrs else ''
            }
        except:
            return None
        

    def fetch_data(self, entity_type, entity_name):
        # Imprimir el estado del caché para este tipo de entidad antes de hacer nada
        print(f"Estado del caché para {entity_type}: {list(self.cache[entity_type].keys())}")
        
        # Corregir nombre
        original_name = entity_name
        corrected_name = self.correct_entity_name(
                                                name=entity_name.lower().replace(" ", "_"),
                                                entity_type=entity_type
                                                )
        entity_name = corrected_name
        
        # Mostrar la transformación del nombre para depuración
        print(f"Nombre original: {original_name} -> Nombre corregido: {entity_name}")
    
        # Verificar caché primero con información detallada
        print(f"Buscando en caché: {entity_type}:{entity_name}")
        if entity_name in self.cache[entity_type]:
            print(f"✅ Cache hit: {entity_type}:{entity_name}")
            return self.cache[entity_type][entity_name]
        else:
            print(f"❌ Cache miss: {entity_type}:{entity_name}")
            print(f"Claves disponibles en caché: {list(self.cache[entity_type].keys())}")
        
        if entity_type == 'StarWarsCharacter':
            url = f"https://swapi.dev/api/people/?search={entity_name.replace('_', ' ')}"
            print(f'pokemon url: {url}' )
            response = requests.get(url)
            data = response.json()
            response = data.get('results', [{}])[0]
            result = {
                "height": response["height"],
                "mass": response["mass"],
                "homeworld": response["homeworld"]
            }
        elif entity_type == 'StarWarsPlanet':
            url = f"https://swapi.dev/api/planets/?search={entity_name.replace('_', ' ')}"
            print(f'pokemon url: {url}' )
            response = requests.get(url)
            data = response.json()
            response = data.get('results', [{}])[0]
            result = {
                "surface_water": response["surface_water"],
                "rotation_period": response["rotation_period"],
                "population": response["population"],
                "diameter": response["diameter"],
                "orbital_period": response["orbital_period"]
            }
        elif entity_type == 'Pokemon':
            url = f"https://pokeapi.co/api/v2/pokemon/{entity_name.replace('_', '-').lower()}"
            print(f'pokemon url: {url}' )
            response = requests.get(url)
            result = {
                "base_experience": response.json()["base_experience"],
                "height": response.json()["height"],
                "weight": response.json()["weight"]
            }
        else:
            return None
        
        if response.status_code != 200:
            return None
        
        self.cache[entity_type][entity_name] = result
        return result

    def resolve_attribute(self, data, attribute_path):
        current = data
        for attr in attribute_path.split('.'):
            if isinstance(current, dict):
                current = current.get(attr, 0)
                if isinstance(current, str) and current.startswith('http'):
                    current = requests.get(current).json()
            else:
                return 0
        try:
            return float(current)
        except:
            return 0
    
    def submit_solution(self, problem_id, answer):
        solution_url = "https://recruiting.adere.so/challenge/solution"
        payload = {
            "problem_id": problem_id,
            "answer": round(answer, 10)
        }
        response = requests.post(solution_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return response.json()  # Siguiente problema
        else:
            raise Exception(f"Error al enviar solución: {response.text}")

    
    def solve_problem(self, problem_text):
        try:
            expression = self.get_expression_from_ai(problem_text)
            print(f"Expression entera: {expression}")
            expression = self.extract_expression(expression)
            print(f"Expression extraida: {expression}")
            terms = re.findall(r'\b\w+:\w+(?:\.\w+)*\b', expression)
            term_values = {}
            for term in terms:
                term_info = self.parse_term(term)
                if not term_info:
                    continue
                data = self.fetch_data(term_info['type'], term_info['name'])
                value = self.resolve_attribute(data, term_info['attribute_path'])
                term_values[term] = value
                print(f"value: {value} - term: {term}")
            
            for term, value in term_values.items():
                expression = expression.replace(term, str(value))
            
            print(f"Calculo: {expression}")
            return eval(expression)
        except:
            return 0
        
    def start_test(self, url):
        response = requests.get(url , headers=self.headers)
        data = response.json()
        problem_id = data['id']
        problem_text = data['problem']
        problem_expression = data['expression']
        problem_solution = data['solution']
        return problem_id, problem_text, problem_expression, problem_solution
    
    def start(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        self.start_time = datetime.now()
        return data['id'], data['problem']
    
    def run_test(self, url):
        problem_id, problem_text, problem_expression, problem_solution = self.start_test(url)
        answer = self.solve_problem(problem_text)
        self.save_cache()
        print(f"Problem ID: {problem_id}")
        print(f"Problem Text: {problem_text}")
        print(f"Problem Expression: {problem_expression}")
        print(f"Problem Solution: {problem_solution}")
        print(f"Answer: {answer}")
        
    def run(self, url):
        problem_id, problem_text = self.start(url)
        total_problem = 0
        while (datetime.now() - self.start_time).seconds < self.time_limit:
            answer = self.solve_problem(problem_text)
            try:
                next_problem_response = self.submit_solution(problem_id, answer)
                print(next_problem_response)
                total_problem += 1
                print(f"Problema {total_problem}")
                next_problem = next_problem_response['next_problem']
                problem_id = next_problem['id']
                problem_text = next_problem['problem']
            except Exception as e:
                print(f"Error: {e}")
                break

token = '4303dd47-5a4d-46f5-81c8-900f26a40c5a'
url_test = 'https://recruiting.adere.so/challenge/test'
url_start = 'https://recruiting.adere.so/challenge/start'
solver = ChallengeSolver(token)
#solver.run(url_start)
solver.run_test(url_test)
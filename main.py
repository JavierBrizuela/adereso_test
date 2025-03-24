import requests
import re
import os
import json
import time
from difflib import get_close_matches
from datetime import datetime
from prompt import PROMPT
from cache_handler import fetch_pokemon_names, fetch_sw_characters, fetch_sw_planets, load_cache, save_cache

class ChallengeSolver:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.cache_file = "api_cache.json"
        self.cache = load_cache(self.cache_file)
        self.pokemon_names = fetch_pokemon_names()
        self.star_wars_characters = fetch_sw_characters()
        self.star_wars_planets = fetch_sw_planets()
        self.start_time = None
        self.time_limit = 180  # 3 minutos en segundos                
        
    def correct_entity_name(self, name, entity_type):
        if entity_type == "Pokemon":
            valid_names = self.pokemon_names
        elif entity_type == "StarWarsCharacter":
            valid_names = self.star_wars_characters
        elif entity_type == "StarWarsPlanet":
            valid_names = self.star_wars_planets
        else:
            return name

        corrected = get_close_matches(name, valid_names, n=1, cutoff=0.5)
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
                        "content": PROMPT
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
            name = self.correct_entity_name(original_name, type_part)
            print(f"nombre correjido: {name}") 
            # Validación cruzada de tipo
            validated_type = self.validate_entity_type(name, type_part)
            print(f"tipo validado: {validated_type}")
            # Si el tipo cambió, volver a corregir el nombre con el tipo validado
            if validated_type != type_part:
                name = self.correct_entity_name(original_name, validated_type)
                print(f"type correjido: {type_part} - name correjido: {name} - attrs correjido: {attrs}")
            return {
                'type': validated_type,
                'name': name,
                'attribute_path': attrs if attrs else ''
            }
            
        except:
            return None
        

    def fetch_data(self, entity_type, entity_name):
       
        # Verificar caché primero
        print(f"Buscando en caché: {entity_type}:{entity_name}")
        if entity_name in self.cache[entity_type]:
            print(f"✅ Cache hit: {entity_type}:{entity_name}")
            return self.cache[entity_type][entity_name]
        else:
            print(f"❌ Cache miss: {entity_type}:{entity_name}")
        
        # Hacer consulta a la api correspondiente
        if entity_type == 'StarWarsCharacter':
            url = f"https://swapi.dev/api/people/?search={entity_name.replace('_', ' ')}"
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
            response = requests.get(url)
            response = response.json()
            result = {
                "base_experience": response["base_experience"],
                "height": response["height"],
                "weight": response["weight"]
            }
            
        else:
            return None
        # Guardar en cache las nuevas entidades
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
        # Enviar solucion
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
            terms = re.findall(r'\b\w+:[\w\-]+(?:\.\w+)*\b', expression)
            term_values = {}
            for term in terms:
                term_info = self.parse_term(term)
                if not term_info:
                    continue
                data = self.fetch_data(term_info['type'], term_info['name'])
                print(f"respuesta de fetch {data}")
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
        return data['id'], data['problem'], data['expression'], data['solution']
        
    
    def run_test(self, url):
        problem_id, problem_text, problem_expression, problem_solution = self.start_test(url)
        answer = self.solve_problem(problem_text)
        answer = round(answer, 10)
        save_cache(self.cache_file, self.cache)
        print(f"Problem ID: {problem_id}")
        print(f"Problem Text: {problem_text}")
        print(f"Problem Expression: {problem_expression}")
        print(f"Problem Solution: {problem_solution}")
        print(f"Answer: {answer}")
        
    def start(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        self.start_time = datetime.now()
        return data['id'], data['problem']
    
    def run(self, url):
        problem_id, problem_text = self.start(url)
        total_problem = 0
        while (datetime.now() - self.start_time).seconds < self.time_limit:
            answer = self.solve_problem(problem_text)
            try:
                next_problem_response = self.submit_solution(problem_id, answer)
                print(next_problem_response)
                save_cache(self.cache_file, self.cache)
                next_problem = next_problem_response['next_problem']
                problem_id = next_problem['id']
                problem_text = next_problem['problem']
            except Exception as e:
                print(f"Error: {e}")
                break

token = os.getenv('TOKEN')
url_test = 'https://recruiting.adere.so/challenge/test'
url_start = 'https://recruiting.adere.so/challenge/start'
solver = ChallengeSolver(token)
solver.run(url_start)
#solver.run_test(url_test)
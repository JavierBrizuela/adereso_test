import requests
import re
import time
from datetime import datetime, timedelta

class ChallengeSolver:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.cache = {}
        self.start_time = None
        self.time_limit = 180  # 3 minutos en segundos
    
    def get_expression_from_ai(self, problem_text):
        chat_url = "https://recruiting.adere.so/chat_completion"
        messages = [
            {
                "role": "system",
                "content": (
                    "Traduce el problema a una expresión matemática usando atributos de Star Wars (Personaje/Planeta) y Pokémon. "
                    "Formato: [Tipo:Nombre.Atributo]. Tipos: StarWarsCharacter, StarWarsPlanet, Pokemon. "
                    "Ejemplo: 'Luke Skywalker masa' → StarWarsCharacter:luke_skywalker.mass"
                )
            },
            {"role": "user", "content": problem_text}
        ]
        payload = {"model": "gpt-4o-mini", "messages": messages}
        response = requests.post(chat_url, headers=self.headers, json=payload)
        return response.json()['choices'][0]['message']['content']
    
    def parse_term(self, term):
        try:
            type_part, rest = term.split(':', 1)
            name, *attrs = rest.split('.', 1)
            return {
                'type': type_part,
                'name': name,
                'attribute_path': attrs[0] if attrs else ''
            }
        except:
            return None
        
    def fetch_data(self, entity_type, entity_name):
        cache_key = (entity_type, entity_name)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if entity_type == 'StarWarsCharacter':
            url = f"https://swapi.dev/api/people/?search={entity_name.replace('_', ' ')}"
        elif entity_type == 'StarWarsPlanet':
            url = f"https://swapi.dev/api/planets/?search={entity_name.replace('_', ' ')}"
        elif entity_type == 'Pokemon':
            url = f"https://pokeapi.co/api/v2/pokemon/{entity_name.replace('_', '-').lower()}"
        else:
            return None
        
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        data = response.json()
        result = data.get('results', [{}])[0] if entity_type != 'Pokemon' else data
        self.cache[cache_key] = result
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
    
    def solve_problem(self, problem_text):
        try:
            expression = self.get_expression_from_ai(problem_text)
            terms = re.findall(r'\b\w+:\w+(?:\.\w+)*\b', expression)
            term_values = {}
            print(f"Expression: {expression}")
            for term in terms:
                term_info = self.parse_term(term)
                if not term_info:
                    continue
                data = self.fetch_data(term_info['type'], term_info['name'])
                value = self.resolve_attribute(data, term_info['attribute_path'])
                term_values[term] = value
            print(f"term_values: {term_values}")
            
            for term, value in term_values.items():
                expression = expression.replace(term, str(value))
            print(f"Expression: {expression}")
            return eval(expression)
        except:
            return 0
        
    def run_test(self, url):
        problem_id, problem_text, problem_expression, problem_solution = self.start_test(url)
        answer = self.solve_problem(problem_text)
        print(f"Problem ID: {problem_id}")
        print(f"Problem Text: {problem_text}")
        print(f"Problem Expression: {problem_expression}")
        print(f"Problem Solution: {problem_solution}")
        print(f"Answer: {answer}")
        
    def run(self, url):
        problem_id, problem_text = self.start(url)
        while (datetime.now() - self.start_time).seconds < self.time_limit:
            answer = self.solve_problem(problem_text)
            try:
                next_problem = self.submit_solution(problem_id, answer)
                problem_id = next_problem['id']
                problem_text = next_problem['problem']
            except Exception as e:
                print(f"Error: {e}")
                break

token = '4303dd47-5a4d-46f5-81c8-900f26a40c5a'
url_test = 'https://recruiting.adere.so/challenge/test'
url_start = 'https://recruiting.adere.so/challenge/start'
solver = ChallengeSolver(token)
solver.run_test(url_test)
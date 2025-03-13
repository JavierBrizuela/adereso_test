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
        
    def start_test(self, url):
        response = requests.get(url , headers=self.headers)
        data = response.json()
        problem_id = data['id']
        problem_text = data['problem'],
        problem_expression = data['expression']
        problem_solution = data['solution']
        print(data)
        return problem_id, problem_text, problem_expression, problem_solution
    
    def run(self, url, test=False):
        if test:
            problem_id, problem_text, problem_expression, problem_solution = self.start_test(url)
            print(f"Problem ID: {problem_id}")
            print(f"Problem Text: {problem_text}")
            print(f"Problem Expression: {problem_expression}")
            print(f"Problem Solution: {problem_solution}")
        else:
            self.start_time = datetime.now()
            self.solve(url)

token = '4303dd47-5a4d-46f5-81c8-900f26a40c5a'
url_test = 'https://recruiting.adere.so/challenge/test'
url_start = 'https://recruiting.adere.so/challenge/start'
solver = ChallengeSolver(token)
solver.run(url_test, test=True)
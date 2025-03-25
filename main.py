import os
from chalengeSolver.chalenge_solver import ChallengeSolver

token = os.getenv('TOKEN')
url_test = 'https://recruiting.adere.so/challenge/test'
url_start = 'https://recruiting.adere.so/challenge/start'
solver = ChallengeSolver(token)
#solver.run(url_start) # Iniciar la prueba 
solver.run_test(url_test) # Resolver un problema de prueba
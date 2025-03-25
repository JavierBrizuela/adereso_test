# 🌌 SWAPI & PokéAPI Challenge Solver

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![SWAPI](https://img.shields.io/badge/SWAPI-v2.0.0-green)](https://swapi.dev/)
[![PokeAPI](https://img.shields.io/badge/PokeAPI-v2.0-orange)](https://pokeapi.co/)
[![OpenAI](https://img.shields.io/badge/GPT-4o--mini-purple?logo=openai)](https://openai.com/)

Solución automatizada para resolver problemas matemáticos basados en atributos de:
- Personajes y Planetas de Star Wars (SWAPI)
- Pokémon (PokeAPI)

**Flujo del proyecto**:  
`Problema en lenguaje natural → Interpreta y genera una expresion matematica con IA → Consulta APIs → Cálculo → Respuesta`

---

## 🚀 Características clave
- **Interpretación de problemas**: Usa GPT-4o-mini para convertir enunciados en expresiones matemáticas
- **Manejo de APIs**: Consultas concurrentes a SWAPI y PokeAPI con caché integrado
- **Resiliencia**:  
  - Corrección de nombres (ej: `polihwirl` → `poliwhirl`, `surface_water` → `surfac_water`)  
  - Corrección de clasificación Errónea (ej: `Volcanion` no pertenece a `StarWarsCharacter`)  
- **Optimización**: Tiempo promedio de respuesta < 4 segundos por problema

---

## 🛠️ Stack tecnológico
| **Componente**       | **Tecnologías**                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| Lenguaje principal    | Python 3.10                                                                     |
| APIs consumidas       | SWAPI, PokeAPI                                                                  |
| IA Generativa         | GPT-4o-mini (via proxy de Adereso)                                              |
| Almacenamiento        | Caché en memoria + persistente en JSON                                          |

---

## ⚙️ Configuración

1. **Clonar repositorio**:
```bash
git clone https://github.com/tu-usuario/swapi-pokeapi-solver.git
cd swapi-pokeapi-solver

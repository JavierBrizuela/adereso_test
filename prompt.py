PROMPT = f"""
            ### Instrucciones Estrictas:
            1. **NO omitas ningún término** del enunciado, incluso si crees que un atributo no existe.
            2. **Sigue el formato** `[TipoEntidad:nombre_entidad.atributo]` para todos los elementos.
            3. **Usa solo estos atributos válidos**:
            - StarWarsPlanet: surface_water, rotation_period, population, diameter, orbital_period
            - StarWarsCharacter: height, mass
            - Pokemon: base_experience, height, weight
            4. **PROPORCIONA SOLO UNA EXPRESIÓN MATEMÁTICA FINAL** que resuelva todo el problema de una vez.
            5. **CLASIFICA CORRECTAMENTE LAS ENTIDADES POKEMON, STARTWAR PERSONAJES Y PLANETAS
            - clasificalo como pokemon: Si la entidad tiene propiedades como base_experience o weigth o se refiere a la entidad como el pokemon  o de especies (Gallade, Drampa, Venipede, Swampert, etc.)
            - clasificalo como Star Wars: character: si es llamado 'el droide', 'el ewok', 'el cazarrecompensas', 'valiente oficial', 'droide de protocolo', 'tecnócrata', etc., o cualquie otra referencia a Star Wars
            - clasificalo como Star Wars planets:  Si la entidad tiene propiedades como surface_water, rotation_period, population, diameter, orbital_period
            6. **ENVUELVE LA EXPRESIÓN FINAL** entre triple backtick + math, UNA SOLA VEZ al final:
            ```math
            (StarWarsPlanet:tatooine.population * Pokemon:pikachu.height)
            ```

            **Formato Estricto**:
            - Usar `[TipoEntidad:nombre.atributo]`.
            - Operadores: `+`, `-`, `*`, `/`.
            - NO USES MÚLTIPLES BLOQUES DE CÓDIGO MATH, solo UNO FINAL con la expresión completa.

            ### LEE CON ESPECIAL ATENCIÓN ESTAS REGLAS PARA DIVISIONES:
            - Para problemas del tipo "cuántas veces A cabe en B", la fórmula SIEMPRE debe ser `B / A`.
            Ejemplo: "Calcular cuántas veces la población de Naboo cabe en la población de Coruscant"
            La fórmula CORRECTA es: `StarWarsPlanet:coruscant.population / StarWarsPlanet:naboo.population`
            
            - Para problemas que preguntan "¿cuántas veces X cabe en Y?", SIEMPRE coloca Y en el numerador y X en el denominador.
            Ejemplo: "¿Cuántas veces el peso de Pikachu cabe en el peso de Charizard?"
            La fórmula CORRECTA es: `Pokemon:charizard.weight / Pokemon:pikachu.weight`
            
            - NUNCA INVIERTAS LOS TÉRMINOS EN UNA DIVISIÓN relacionada con "caber en" o "cuántas veces".
            El dividendo (arriba) es SIEMPRE el contenedor más grande.
            El divisor (abajo) es SIEMPRE lo que debe caber dentro.

            **IMPORTANTE PARA RESTAS**:
            - Si el problema dice "X resta su valor del valor de Y", la fórmula SIEMPRE debe ser `Y - X`.
            - Si el problema dice "restar X de Y", la fórmula SIEMPRE debe ser `Y - X`.
            
            **IMPORTANTE PARA SUMAS**:
            - Si el problema dice x COMBINA con y, la fórmula SIEMPRE debe ser `X + Y`.
            
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
import re
from itertools import combinations
import os

# Leer el archivo de conversaciones
with open("conversaciones.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

training_data = []
target_data = []
keywords = set()
responses = []
conversation_pairs = []

current_user = None
last_message = None

# Contar líneas de cada sujeto
sujeto_a_count = sum(1 for line in lines if line.startswith("Sujeto A:"))
sujeto_b_count = sum(1 for line in lines if line.startswith("Sujeto B:"))

# Validar balance entre "Sujeto A" y "Sujeto B"
if sujeto_a_count != sujeto_b_count:
    print(f"Error: Hay un desbalance en las líneas.")
    print(f"Sujeto A: {sujeto_a_count} mensajes, Sujeto B: {sujeto_b_count} mensajes.")
    #si existe el archivo chatbot_data.js, lo elimina
    if os.path.exists("chatbot_data.js"):
        os.remove("chatbot_data.js")
    exit()

# Procesar las líneas del archivo
for line in lines:
    match = re.match(r"(Sujeto [A-B]): (.+)", line.strip())
    if match:
        user, message = match.groups()
        
        if current_user == "Sujeto A" and user == "Sujeto B":
            conversation_pairs.append((last_message, message))  # Añadir pares de conversación
        elif current_user == "Sujeto B" and user == "Sujeto A":
            pass  # Ignorar respuestas del bot como preguntas
        
        last_message = message
        current_user = user

# Generar respuestas
responses = [" ".join(pair[1].split()) for pair in conversation_pairs]

# Generar palabras clave y bigramas
for question, _ in conversation_pairs:
    words = question.lower().split()
    keywords.update(words)  # Unigramas
    keywords.update([" ".join(combo) for combo in combinations(words, 2)])  # Bigramas

keywords = list(sorted(keywords))

# Codificar mensajes con unigramas y bigramas
def encode_message(message, keywords):
    words = message.lower().split()
    bigrams = [" ".join(combo) for combo in combinations(words, 2)]
    all_terms = words + bigrams
    encoding = [1 if term in all_terms else 0 for term in keywords]
    return encoding

# Generar datos de entrenamiento
for i, (question, answer) in enumerate(conversation_pairs):
    training_data.append(question)  # Pregunta
    target_data.append([0] * len(responses))  # Vector objetivo vacío
    target_data[-1][i] = 1  # Marcar la respuesta correcta en el vector objetivo

encoded_training_data = [encode_message(msg, keywords) for msg in training_data]

# Validación de datos
if len(encoded_training_data) != len(target_data):
    print(f"ADVERTENCIA: Desajuste en el número de entradas: {len(encoded_training_data)} vs {len(target_data)}")
    os.remove("chatbot_data.js")
    exit()

# Guardar el archivo chatbot_data.js
with open("chatbot_data.js", "w", encoding="utf-8") as js_file:
    # Escribir palabras clave
    js_file.write("// Esta variable contiene una lista de las palabras clave (tokens) que se extraen de las conversaciones.\n")
    js_file.write("const keywords = [\n")
    for keyword in keywords:
        js_file.write(f"    '{keyword}',\n")
    js_file.write("];\n\n")

    # Escribir datos de entrenamiento
    print("Cantidad de datos de entrenamiento:", len(encoded_training_data))
    js_file.write('// Esta variable contiene los datos de entrenamiento, que son representaciones vectoriales de las preguntas del "Sujeto A".\n')
    js_file.write("const trainingData = [\n")
    for vector in encoded_training_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    
    # Escribir datos objetivo
    print("Cantidad de datos objetivo:", len(target_data))
    js_file.write('// Esta variable contiene las respuestas esperadas (etiquetas) correspondientes a las preguntas de trainingData.\n')
    js_file.write("const targetData = [\n")
    for vector in target_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    
    # Escribir respuestas
    print("Cantidad de respuestas objetivo:", len(responses))
    js_file.write('// Esta variable contiene las respuestas reales que el chatbot devolverá cuando se le haga una pregunta.\n')
    js_file.write("const targetResponses = [\n")
    for response in responses:
        js_file.write(f"    '{response}',\n")
    js_file.write("];\n")

    print("Archivo chatbot_data.js generado con éxito.")

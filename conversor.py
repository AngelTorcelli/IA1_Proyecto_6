import re
import json

# Leer el archivo de texto
with open("conversaciones.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Inicializar listas y variables
training_data = []
target_data = []
keywords = set()
responses = []
conversation_pairs = []

current_user = None
last_message = None

# Crear pares de conversaciones (A pregunta, B responde)
for line in lines:
    match = re.match(r"(Sujeto [A-B]): (.+)", line.strip())
    if match:
        user, message = match.groups()
        
        if current_user == "Sujeto A" and user == "Sujeto B":
            # Si Sujeto A hace una pregunta, Sujeto B debe responder
            conversation_pairs.append((last_message, message))  # Emparejamos pregunta de A con respuesta de B
        elif current_user == "Sujeto B" and user == "Sujeto A":
            # Si Sujeto B hace una respuesta, Sujeto A debe hacer la siguiente pregunta
            pass
        
        # Guardamos el último mensaje de A para emparejarlo con la respuesta de B
        last_message = message
        
        current_user = user

# Ahora extraemos las respuestas únicas
responses = [" ".join(pair[1].split()) for pair in conversation_pairs]  # Solo las respuestas de Sujeto B

# Procesar las parejas de conversación
for i, (question, answer) in enumerate(conversation_pairs):
    training_data.append(question)  # Mensaje de Sujeto A (pregunta)
    target_data.append([0] * len(responses))  # Inicializamos un vector de ceros con el tamaño de las respuestas
    target_data[-1][i] = 1  # Marcamos el índice correspondiente a la respuesta correcta
    keywords.update(question.lower().split())  # Extraer palabras clave de la pregunta

keywords = list(sorted(keywords))

# Codificar los datos
def encode_message(message, keywords):
    encoding = [1 if word in message.lower().split() else 0 for word in keywords]
    return encoding

encoded_training_data = [encode_message(msg, keywords) for msg in training_data]

# Verificar que training_data y target_data tienen la misma longitud
if len(encoded_training_data) != len(target_data):
    print(f"ADVERTENCIA: Desajuste en el número de entradas: {len(encoded_training_data)} vs {len(target_data)}")

# Generar el archivo JS
with open("chatbot_data.js", "w", encoding="utf-8") as js_file:
    js_file.write("//Esta variable contiene una lista de las palabras clave (tokens) que se extraen de las conversaciones.\n")
    js_file.write("const keywords = [\n")
    for keyword in keywords:
        js_file.write(f"\t'{keyword}',\n")  # Escribe cada palabra clave en una nueva línea
    js_file.write("];\n\n")  # Cierra la lista con un salto de línea después

    
    # Escribir trainingData con saltos de línea
    print("Cantidad de datos de entrenamiento:", len(encoded_training_data))
    js_file.write('//Esta variable contiene los datos de entrenamiento, que son representaciones vectoriales de las preguntas del "Sujeto A"\n')
    js_file.write("const trainingData = [\n")
    for vector in encoded_training_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    
    # Escribir targetData con saltos de línea
    print("Cantidad de datos objetivo:", len(target_data))
    js_file.write('//Esta variable contiene las respuestas esperadas (etiquetas) correspondientes a las preguntas de trainingData\n')
    js_file.write("const targetData = [\n")
    for vector in target_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    
    # Escribir targetResponses con saltos de línea
    print("Cantidad de respuestas objetivo:", len(responses))
    js_file.write('//Esta variable contiene las respuestas reales que el chatbot devolverá cuando se le haga una pregunta.\n')
    js_file.write("const targetResponses = [\n")
    for response in responses:
        js_file.write(f"    '{response}',\n")
    js_file.write("];\n")

    print("Archivo chatbot_data.js generado con éxito.")

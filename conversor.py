import re

with open("conversaciones.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

training_data = []
target_data = []
keywords = set()
responses = []
conversation_pairs = []

current_user = None
last_message = None

for line in lines:
    match = re.match(r"(Sujeto [A-B]): (.+)", line.strip())
    if match:
        user, message = match.groups()
        
        if current_user == "Sujeto A" and user == "Sujeto B":
            conversation_pairs.append((last_message, message)) 
        elif current_user == "Sujeto B" and user == "Sujeto A":
            pass
        
        last_message = message
        
        current_user = user

responses = [" ".join(pair[1].split()) for pair in conversation_pairs] 


for i, (question, answer) in enumerate(conversation_pairs):
    training_data.append(question)  
    target_data.append([0] * len(responses))  
    target_data[-1][i] = 1 
    keywords.update(question.lower().split()) 

keywords = list(sorted(keywords))


def encode_message(message, keywords):
    encoding = [1 if word in message.lower().split() else 0 for word in keywords]
    return encoding

encoded_training_data = [encode_message(msg, keywords) for msg in training_data]

if len(encoded_training_data) != len(target_data):
    print(f"ADVERTENCIA: Desajuste en el número de entradas: {len(encoded_training_data)} vs {len(target_data)}")


with open("chatbot_data.js", "w", encoding="utf-8") as js_file:
    js_file.write("//Esta variable contiene una lista de las palabras clave (tokens) que se extraen de las conversaciones.\n")
    js_file.write("const keywords = [\n")
    for keyword in keywords:
        js_file.write(f"\t'{keyword}',\n") 
    js_file.write("];\n\n")  

    
   
    print("Cantidad de datos de entrenamiento:", len(encoded_training_data))
    js_file.write('//Esta variable contiene los datos de entrenamiento, que son representaciones vectoriales de las preguntas del "Sujeto A"\n')
    js_file.write("const trainingData = [\n")
    for vector in encoded_training_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    

    print("Cantidad de datos objetivo:", len(target_data))
    js_file.write('//Esta variable contiene las respuestas esperadas (etiquetas) correspondientes a las preguntas de trainingData\n')
    js_file.write("const targetData = [\n")
    for vector in target_data:
        js_file.write("    " + str(vector) + ",\n")
    js_file.write("];\n\n")
    

    print("Cantidad de respuestas objetivo:", len(responses))
    js_file.write('//Esta variable contiene las respuestas reales que el chatbot devolverá cuando se le haga una pregunta.\n')
    js_file.write("const targetResponses = [\n")
    for response in responses:
        js_file.write(f"    '{response}',\n")
    js_file.write("];\n")

    print("Archivo chatbot_data.js generado con éxito.")

import tkinter as tk
from tkinter import scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer  # Importar TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
import unicodedata
import re
import pandas as pd
from idioma_chat import detectar_lang, traducir

lang_envio = "en"

# Cargar el archivo de preguntas y respuestas
df = pd.read_csv("chat_data.csv", delimiter=";")
#df = pd.read_csv("preguntas.csv", delimiter=";")

# Descargar recursos necesarios de nltk
""" nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
 """
# Inicializar el Stemmer y el Lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Función para eliminar tildes
def remove_accents(text):
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Función para eliminar caracteres no alfabéticos
def remove_non_alphabets(text):
    return re.sub(r'[^a-záéíóúñ\s]', '', text)

# Función para preprocesar el texto
def preprocess_text(text):
    text = text.lower()  # Convertir a minúsculas
    text = remove_accents(text)  # Eliminar tildes
    text = remove_non_alphabets(text)  # Eliminar caracteres no alfabéticos
    
    tokens = nltk.word_tokenize(text)  # Tokenizar
    stemmed_tokens = [stemmer.stem(token) for token in tokens]  # Stemming
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos=wordnet.VERB) for token in stemmed_tokens]  # Lemmatización
    return " ".join(lemmatized_tokens)

# Preprocesar las preguntas
print("Preprocesando las preguntas...")
#X = [preprocess_text(text) for text in df['PREGUNTA']]  # Preprocesar preguntas
X = df['PREGUNTA']  # Preguntas
y = df['RESPUESTA']  # Respuestas
print("Preprocesamiento completado.")

# Convertir texto a características numéricas usando TF-IDF
print("Convirtiendo las preguntas a características numéricas usando TF-IDF...")
vectorizer = TfidfVectorizer(stop_words="english", max_features=1000, ngram_range=(1, 2))  # Configuración de TF-IDF
X_vectors = vectorizer.fit_transform(X)
print("Conversión a características numéricas completada.")

# Entrenar el modelo
print("Entrenando el modelo...")
model = MultinomialNB() # se puede cambiar el valor de alpha o quitarlo
model.fit(X_vectors, y)
print("Modelo entrenado con éxito.")

# Función para predecir la respuesta
def get_response(user_input):
    user_input_preprocessed = preprocess_text(user_input)
    input_vector = vectorizer.transform([user_input_preprocessed])
    
    # Obtener las probabilidades para todas las clases
    probabilities = model.predict_proba(input_vector)
    
    # Obtener la probabilidad más alta y su clase correspondiente
    max_probability = probabilities.max()
    max_class_index = probabilities.argmax()
    predicted_class = model.classes_[max_class_index]
    
    # Mostrar probabilidad más alta y clase correspondiente
    print(f"Probabilidad más alta: {max_probability:.2f} para la clase: {predicted_class}")
    
    """ # Devolver la predicción si supera el umbral
    if max_probability < 0.30:
        return "Lo siento, no entiendo tu pregunta." """
    return predicted_class

# Función para mostrar un mensaje en el área de texto
def display_message(message, side):
    message_area.config(state=tk.NORMAL)

    message_area.insert(tk.END, f"{message}\n", "right_message")
    message_area.yview(tk.END)
    message_area.config(state=tk.DISABLED)

# Función para enviar un mensaje
def send_message(event=None):
    if send_button['state'] == 'normal':
        message = message_entry.get()
        if message.strip():
            display_message("\n👤: " + message+" ", "right")
            msj_bot=get_response(message)
            l=detectar_lang(message)
            if l!=lang_envio:
                message=traducir(message)
                msj_bot=get_response(message)

            msj_final=msj_bot if l==lang_envio else traducir(msj_bot)
            message_entry.delete(0, tk.END)
            disable_send_button()
            receive_message("🤖: " + msj_final)


def validar_texto(texto):
    # Lista para almacenar las partes del texto procesado
    resultado = []
    
    # Utilizamos re.finditer para buscar partes dentro y fuera de '|'
    partes = re.finditer(r'(\|([^|]+)\|)|([^|]+)', texto)
    
    # Procesamos cada coincidencia
    for match in partes:
        if match.group(2):  # Si el texto está entre '|', group(2) tendrá el texto entre las barras
            resultado.append(f"☺{match.group(2).strip()} ")
        elif match.group(3):  # Si no está entre '|', group(3) tendrá el texto fuera de las barras
            resultado.append(match.group(3).strip()+" ")

    return [elemento.replace("\\n", "\n").replace("\\t","\t") for elemento in resultado]

# Función para recibir un mensaje con manejo secuencial de texto
def receive_message(message):
    message_area.config(bg="gray90")
    vt = validar_texto(message)  # Lista de partes del texto procesado
    #print(vt, "tamaño: ", len(vt))
    process_vt(vt, 0)  # Procesa los elementos de vt uno por uno

# Función para procesar secuencialmente los elementos de vt
def process_vt(vt, index):
    if index < len(vt):  # Si quedan elementos por procesar
        typing_effect(vt[index], 0, lambda: process_vt(vt, index + 1))
    else:
        enable_send_button()  # Habilitar el botón después de terminar todos los mensajes

# Función para mostrar el efecto de tipeo en un solo mensaje
def typing_effect(message, index, callback=None):
    if index < len(message):
        message_area.config(state=tk.NORMAL)
        char = message[index]

        # Si contiene ☺, aplica el formato especial
        if "☺" in message:
            formatted_char = char.replace("☺", "")  # Eliminar el símbolo ☺
            message_area.insert(tk.END, formatted_char, "code")
        else:
            message_area.insert(tk.END, char, "left_message")
        
        message_area.config(state=tk.DISABLED)
        message_area.yview(tk.END)
        
        # Continuar escribiendo el siguiente carácter
        root.after(20, typing_effect, message, index + 1, callback)
    else:
        # Cuando termina de escribir el mensaje, llama al callback
        if callback:
            callback()
        message_area.config(state=tk.NORMAL)
        #message_area.insert(tk.END, "\n")
        message_area.config(state=tk.DISABLED)


# Habilitar/deshabilitar botón de enviar
def disable_send_button():
    message_entry.config(state=tk.DISABLED)
    send_button.config(state=tk.DISABLED)

def enable_send_button():
    send_button.config(state=tk.NORMAL)
    message_entry.config(state=tk.NORMAL)

# Configurar la ventana principal
root = tk.Tk()
root.title("UsatBot")
width, height = 700, 600
x, y = (root.winfo_screenwidth() // 2 - width // 2, root.winfo_screenheight() // 2 - height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.resizable(False, False)

# Marco principal
frame_main = tk.Frame(root)
frame_main.pack(fill="both", expand=True)

# Área de texto
frame_messages = tk.Frame(frame_main)
frame_messages.pack(padx=10, pady=10, fill="both", expand=True)
message_area = scrolledtext.ScrolledText(frame_messages, wrap=tk.WORD, width=40, height=20, state=tk.DISABLED)
message_area.pack(padx=10, pady=10, fill="both", expand=True)
message_area.tag_configure("red", foreground="red", background="yellow")

# Entrada de texto
frame_input = tk.Frame(frame_main)
frame_input.pack(pady=10, fill="x", expand=True)
message_entry = tk.Entry(frame_input, width=30, font=("Arial", 14))
message_entry.pack(side=tk.LEFT, padx=50, fill="x", expand=True)
message_entry.bind("<Return>", send_message)
message_entry.focus()

# Botón enviar
send_button = tk.Button(frame_input, text="Enviar", command=send_message, font=("Arial", 14))
send_button.pack(side=tk.LEFT, padx=(0, 100))

# Configuración de mensajes
message_area.tag_configure("left_message", justify="left", foreground="black", font=("Arial", 14, "bold"))
message_area.tag_configure("code", justify="left", foreground="green", font=("Consolas", 14, "italic"))
message_area.tag_configure("right_message", justify="right", foreground="blue", font=("Arial", 14, "bold"))

# Ejecutar la aplicación
root.mainloop()

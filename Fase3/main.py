import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer  # Importar TfidfVectorizer
import pandas as pd
from idioma_chat import detectar_lang, traducir

from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher
import re
import joblib
import os
lang_envio = "en"

class ProgrammingChatbot:
    def __init__(self, initial_data_path, user_data_path='chat_data_user.csv',  similarity_threshold=0.3, exact_match_threshold=0.9, vectorizer_path='tfidf_vectorizer.pkl'):
        self.similarity_threshold = similarity_threshold  # Umbral para considerar respuestas similares
        self.exact_match_threshold = exact_match_threshold  # Umbral para considerar respuestas exactas        
        self.lemmatizer = WordNetLemmatizer()
        self.user_data_path = user_data_path

        # Verificar si existe el archivo personalizado
        if os.path.exists(user_data_path):
            print(f"Using existing user data from {user_data_path}")
            self.load_model(vectorizer_path, user_data_path)
        elif os.path.exists(initial_data_path):
            print(f"Entrenando con la data inicial en {initial_data_path}")
            self.load_data(initial_data_path)
            self.prepare_vectorizer()
            self.save_model(vectorizer_path, user_data_path)
        else:
            raise FileNotFoundError("No valid data file found to train the chatbot.")
    
    def load_data(self, data_path):
        #para cargar los datos iniciales
        self.df = pd.read_csv(data_path, delimiter='~')
        
        self.df = self.df.dropna(subset=['PREGUNTA', 'RESPUESTA'])
        self.df['PREGUNTA'] = self.df['PREGUNTA'].astype(str) 
        
        self.df['processed_question'] = self.df['PREGUNTA'].apply(self.preprocess_text)

    def add_training_data(self, question, answer):
        """Add new training data and update the model"""
        new_data = pd.DataFrame({'PREGUNTA': [question], 'RESPUESTA': [answer]})
        self.df = pd.concat([self.df, new_data], ignore_index=True)
        self.df.loc[len(self.df) - 1, 'processed_question'] = self.preprocess_text(question)
        self.prepare_vectorizer()
        
        # Guardar los datos actualizados en el archivo personalizado
        self.save_training_data(self.user_data_path)

    def save_training_data(self, filepath):
        """esto es para guardar los datos de entrenamiento en un archivo CSV, se usa para actualizar el modelo"""
        self.df[['PREGUNTA', 'RESPUESTA']].to_csv(filepath, sep='~', index=False)

    def save_model(self, vectorizer_path, data_path):
        """Guardar el vectorizador y los datos procesados, el vectorizador sirve para transformar las preguntas en vectores"""
        joblib.dump(self.vectorizer, vectorizer_path)
        self.df.to_csv(data_path, sep='~', index=False)

    def load_model(self, vectorizer_path, data_path):
        """Cargar el vectorizador y los datos procesados"""
        self.vectorizer = joblib.load(vectorizer_path)
        self.df = pd.read_csv(data_path, delimiter='~')
        self.question_vectors = self.vectorizer.transform(self.df['processed_question'])

    def string_similarity(self, str1, str2):
        """Calcula la similitud entre dos strings usando SequenceMatcher"""
        return SequenceMatcher(None, str1, str2).ratio()

    def preprocess_text(self, text):
        
        if pd.isna(text) or not isinstance(text, str):  # Verificar que el texto sea válido
            return ''
        #normalizacion basica
        text = text.lower().strip()
        text = re.sub(r'[^\w\s?]', '', text)        
        
        # Reemplazar contracciones comunes como "what's" -> "whats"
        text = re.sub(r"\'s", "s", text)  # Manejar 's (e.g., what's -> whats)
        text = re.sub(r"\'t", "t", text)  # Manejar 't (e.g., don't -> dont)
        text = re.sub(r"\'re", "re", text)  # Manejar 're (e.g., you're -> youre)
        text = re.sub(r"\'ll", "ll", text)  # Manejar 'll (e.g., I'll -> Ill)
        text = re.sub(r"\'ve", "ve", text)  # Manejar 've (e.g., I've -> Ive)
        text = re.sub(r"\'d", "d", text)  # Manejar 'd (e.g., I'd -> Id)
        text = re.sub(r"\'", "", text)  # Eliminar apóstrofes restantes
        
        text = re.sub(r'[^\w\s]', '', text)
        
        #tokenizacion
        tokens = word_tokenize(text)
        
        stop_words = set(stopwords.words('english')) - {
            'how', 'what', 'why', 'which', 'you', 'this', 'who',
            'can','do','no','here','more','up','not','where','there',
            'about','while','doing', 'is', 'are', 'was', 'were', 'will', 'do', 'does', 'did',
            'can', 'could', 'should', 'would', 'may', 'might'
        }
        tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatization
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # esto es para reemplazar los términos de programación con palabras clave más comunes
        programming_terms = {
            'js': 'javascript',
            'py': 'python',
            'func': 'function',
            'var': 'variable',
            'dict': 'dictionary',
            'arr': 'array',
            'obj': 'object',
            'str': 'string',
            'num': 'number',
            'bool': 'boolean',
            'exc': 'exception',
            'err': 'error',
            'lib': 'library',
            'pkg': 'package',
            'dir': 'directory',
            'prop': 'property',
            'param': 'parameter',
            'arg': 'argument',
            'const': 'constant',
            'def': 'define',
            
        }
        tokens = [programming_terms.get(token, token) for token in tokens]
        processed_text = ' '.join(tokens)
        #print(f"Preprocessed: '{text}' -> '{processed_text}'")  # Depuración
        return processed_text
    
    def find_similar_questions(self, processed_input):
        # Vector de la pregunta del usuario
        input_vector = self.vectorizer.transform([processed_input])
        
        # Similitud del coseno
        cosine_similarities = cosine_similarity(input_vector, self.question_vectors).flatten()
        
        # Similitud de strings para cada pregunta
        string_similarities = [
            self.string_similarity(processed_input, q) 
            for q in self.df['processed_question']
        ]
        
        # Combinar similitudes (promedio ponderado)
        combined_similarities = [
            0.4 * cos_sim + 0.6 * str_sim
            for cos_sim, str_sim in zip(cosine_similarities, string_similarities)
        ]
        
        return combined_similarities

    def prepare_vectorizer(self):
        """Initialize and fit the TF-IDF vectorizer"""
        # Stopwords personalizadas
        custom_stopwords = set(stopwords.words('english')) - {'how', 'what', 'why', 'which', 'you', 'this', 'who','can','do','no','here','more','up','not','where','there','about','while','doing'}
        custom_stopwords = list(custom_stopwords)
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            stop_words=custom_stopwords
        )
        self.question_vectors = self.vectorizer.fit_transform(self.df['processed_question'])
        
    def get_response(self, user_input):
        """Obtiene la respuesta más relevante usando similitud mejorada"""
        processed_input = self.preprocess_text(user_input)
        
        # Encuentra similitudes combinadas
        similarities = self.find_similar_questions(processed_input)
        
        best_matches = [
            (similarity, idx) 
            for idx, similarity in enumerate(similarities) 
            if similarity > self.similarity_threshold
        ]
        
        # Ordena por similitud y si hay varias respuestas, elige la mejor
        best_matches.sort(reverse=True)
        
        if not best_matches:
            return self.get_fallback_response(processed_input)
        
        # Si hay una coincidencia muy alta, usa esa respuesta
        if best_matches[0][0] >= self.exact_match_threshold:
            return self.df.iloc[best_matches[0][1]]['RESPUESTA']
        
        # Si hay múltiples coincidencias similares, combina información
        if len(best_matches) > 1:
            top_responses = [
                self.df.iloc[idx]['RESPUESTA']
                for similarity, idx in best_matches[:2]
                if similarity > self.similarity_threshold
            ]
            return self.combine_responses(top_responses, user_input)
        
        return self.df.iloc[best_matches[0][1]]['RESPUESTA']

    def get_fallback_response(self, processed_input):
        """Genera una respuesta cuando no hay coincidencias buenas"""
        programming_terms = [
            'python', 'javascript', 'function', 'variable', 'loop', 'class',
            'array', 'object', 'string', 'number', 'boolean', 'dictionary'
        ]
        
        # Detecta términos de programación en la entrada
        found_terms = [term for term in programming_terms if term in processed_input]
        
        if found_terms:
            return (f"I see you're asking about {', '.join(found_terms)}. "
                   f"Could you rephrase your question to be more specific? "
                   f"For example, you could ask 'What is a {found_terms[0]}?' or "
                   f"'How do I use {found_terms[0]} in Python/JavaScript?'")
        
        return ("I'm sorry, I don't understand your question. "
                "Please make sure it's related to programming, "
                "specifically Python or JavaScript. "
                "Try asking about specific concepts, syntax, or provide code examples.")

    def combine_responses(self, responses, original_question):
        """Combina múltiples respuestas relevantes"""
        # Si las respuestas son muy similares, usa solo la primera
        if self.string_similarity(responses[0], responses[1]) > 0.8:
            return responses[0]
        
        # Combina las respuestas de manera inteligente
        return (f"Let me address your question about '{original_question}' from multiple angles:\n\n"
                f"1. {responses[0]}\n\n"
                f"Additionally:\n2. {responses[1]}")

chatbot = ProgrammingChatbot("chat_data.csv", similarity_threshold=0.4, exact_match_threshold=0.90)
print("Programa cargado correctamente")

# Función para mostrar un mensaje en el área de texto
def display_message(message, side):
    message_area.config(state=tk.NORMAL, bg="#202020")

    message_area.insert(tk.END, f"{message}\n", "right_message")
    message_area.yview(tk.END)
    message_area.config(state=tk.DISABLED, bg="#202020")


def send_message(event=None):
    if send_button['state'] == 'normal':
        message = message_entry.get()
        if message.strip():
            display_message("\n👤: " + message+"\n", "right")
            msj_bot=chatbot.get_response(message)
            l=detectar_lang(message)
            if l!=lang_envio:
                message=traducir(message)
                print("Mensaje traducido: ", message)
                msj_bot=chatbot.get_response(message)

            msj_final=msj_bot if l==lang_envio else traducir(msj_bot)
            message_entry.delete(0, tk.END)
            disable_send_button()
            receive_message("🤖: " + msj_final )


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
    message_area.config(bg="#202020")
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
        message_area.config(state=tk.NORMAL, bg="#202020")
        char = message[index]

        # Si contiene ☺, aplica el formato especial
        if "☺" in message:
            formatted_char = char.replace("☺", "")  # Eliminar el símbolo ☺
            message_area.insert(tk.END, formatted_char, "code")
        else:
            message_area.insert(tk.END, char, "left_message")
        
        message_area.config(state=tk.DISABLED, bg="#202020")
        message_area.yview(tk.END)
        
        # Continuar escribiendo el siguiente carácter
        root.after(10, typing_effect, message, index + 1, callback)
    else:
        # Cuando termina de escribir el mensaje, llama al callback
        if callback:
            callback()
        message_area.config(state=tk.NORMAL, bg="#202020")
        #message_area.insert(tk.END, "\n")
        message_area.config(state=tk.DISABLED, bg="#202020")


# Habilitar/deshabilitar botón de enviar
def disable_send_button():
    message_entry.config(state=tk.DISABLED, bg="#202020")
    send_button.config(state=tk.DISABLED)

def enable_send_button():
    send_button.config(state=tk.NORMAL)
    message_entry.config(state=tk.NORMAL, bg="#202020")

# Configurar la ventana principal
root = tk.Tk()
root.title("UsatBot")
width, height = 700, 600
x, y = (root.winfo_screenwidth() // 2 - width // 2, root.winfo_screenheight() // 2 - height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.resizable(False, False)

root.configure(bg="#202020")
logo = tk.PhotoImage(file="images/logo.png") 
root.iconphoto(False, logo)


# Marco principal
frame_main = tk.Frame(root, bg="#202020")
frame_main.pack(fill="both", expand=True)

# Área de texto
frame_messages = tk.Frame(frame_main, bg="#202020")
frame_messages.pack(padx=10, pady=10, fill="both", expand=True)
message_area = scrolledtext.ScrolledText(frame_messages, wrap=tk.WORD, width=40, height=20,padx=15, pady=15, bg="#2b2b29", fg="#fafafa", state=tk.DISABLED)
message_area.pack(padx=10, pady=10, fill="both", expand=True)
message_area.tag_configure("red", foreground="red", background="yellow")

# Entrada de texto
frame_input = tk.Frame(frame_main, bg="#202020")
frame_input.pack(pady=10, fill="x", expand=True)
message_entry = tk.Entry(frame_input, width=30, font=("calibri", 14), bg="#2b2b29", fg="#fafafa")
message_entry.pack(side=tk.LEFT, padx=(50, 10), pady=5, ipady=8, fill="x", expand=True)
message_entry.bind("<Return>", send_message)
message_entry.focus()

# Botón enviar
send_button = tk.Button(frame_input, text="Enviar", command=send_message, font=("calibri", 14), bg="#0098cc", fg="#fafafa", activebackground="#1E90FF")
send_button.pack(side=tk.LEFT, padx=(10, 50), pady=5, ipady=4)

# Configuración de mensajes
message_area.tag_configure("left_message", justify="left", foreground="#fafafa", font=("calibri", 14))
message_area.tag_configure("code", justify="left", foreground="cyan", font=("Consolas", 14, "italic"))
message_area.tag_configure("right_message", justify="right", foreground="#fafafa", font=("calibri", 14, "bold"))

# Ejecutar la aplicación
root.mainloop()

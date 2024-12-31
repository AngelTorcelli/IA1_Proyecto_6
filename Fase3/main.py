import tkinter as tk
from tkinter import scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer  # Importar TfidfVectorizer
import pandas as pd
from idioma_chat import detectar_lang, traducir

from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import joblib
import os
lang_envio = "en"

class ProgrammingChatbot:
    def __init__(self, initial_data_path, user_data_path='chat_data_user.csv', threshold=0.3, vectorizer_path='tfidf_vectorizer.pkl'):
        self.threshold = threshold
        self.lemmatizer = WordNetLemmatizer()
        self.user_data_path = user_data_path

        # Verificar si existe el archivo personalizado
        if os.path.exists(user_data_path):
            print(f"Using existing user data from {user_data_path}")
            self.load_model(vectorizer_path, user_data_path)
        elif os.path.exists(initial_data_path):
            print(f"Training with initial data from {initial_data_path}")
            self.load_data(initial_data_path)
            self.prepare_vectorizer()
            self.save_model(vectorizer_path, user_data_path)
        else:
            raise FileNotFoundError("No valid data file found to train the chatbot.")
    
    def load_data(self, data_path):
        """Load and preprocess the training data"""
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
        """Save the current training data to a CSV file"""
        self.df[['PREGUNTA', 'RESPUESTA']].to_csv(filepath, sep='~', index=False)

    def save_model(self, vectorizer_path, data_path):
        """Guardar el vectorizador y los datos procesados"""
        joblib.dump(self.vectorizer, vectorizer_path)
        self.df.to_csv(data_path, sep='~', index=False)

    def load_model(self, vectorizer_path, data_path):
        """Cargar el vectorizador y los datos procesados"""
        self.vectorizer = joblib.load(vectorizer_path)
        self.df = pd.read_csv(data_path, delimiter='~')
        self.question_vectors = self.vectorizer.transform(self.df['processed_question'])

    def preprocess_text(self, text):
        """Improved text preprocessing pipeline"""
        
        if pd.isna(text) or not isinstance(text, str):  # Verificar que el texto sea válido
            return ''
        # Lowercase
        text = text.lower()
        
        # Reemplazar contracciones comunes como "what's" -> "whats"
        text = re.sub(r"\'s", "s", text)  # Manejar 's (e.g., what's -> whats)
        text = re.sub(r"\'t", "t", text)  # Manejar 't (e.g., don't -> dont)
        text = re.sub(r"\'re", "re", text)  # Manejar 're (e.g., you're -> youre)
        text = re.sub(r"\'ll", "ll", text)  # Manejar 'll (e.g., I'll -> Ill)
        text = re.sub(r"\'ve", "ve", text)  # Manejar 've (e.g., I've -> Ive)
        text = re.sub(r"\'d", "d", text)  # Manejar 'd (e.g., I'd -> Id)
        text = re.sub(r"\'", "", text)  # Eliminar apóstrofes restantes
        
        text = re.sub(r'[^\w\s]', '', text)
        
        tokens = word_tokenize(text)
        
        # remueve las stopwords pero conserva algunas palabras clave
        stop_words = set(stopwords.words('english')) - {'how', 'what', 'why', 'which', 'you', 'this', 'who','can','do','no','here','more','up','not','where','there','about','while','doing'}
        tokens = [token for token in tokens if token not in stop_words]
        
        # Lemmatization
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # esto es para reemplazar los términos de programación con palabras clave más comunes
        programming_terms = {
            'js': 'javascript',
            'py': 'python',
            'func': 'function',
            'var': 'variable'
        }
        tokens = [programming_terms.get(token, token) for token in tokens]
        processed_text = ' '.join(tokens)
        #print(f"Preprocessed: '{text}' -> '{processed_text}'")  # Depuración
        return processed_text
    
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
        """Get the most relevant response using cosine similarity"""
        # Preprocess the input
        processed_input = self.preprocess_text(user_input)
        
        # vectoriza la pregunta del usuario
        input_vector = self.vectorizer.transform([processed_input])
        
        # Calcula la similitud del coseno entre el vector de entrada y los vectores de preguntas
        similarities = cosine_similarity(input_vector, self.question_vectors)
        
        # esto obtiene la mayor similaridad
        max_similarity = similarities.max()
        
        if max_similarity < self.threshold:
            programming_terms = ['python', 'javascript', 'function', 'variable', 'loop', 'class']
            if any(term in processed_input for term in programming_terms):
                return ("I'm not entirely sure, but I'll try to help. Could you rephrase your question "
                       "or provide more specific details about what you want to know?")
            return ("I'm sorry, I don't understand your question. Please make sure it's related to "
                   "programming, specifically Python or JavaScript.")
        
        best_match_idx = similarities.argmax()
        return self.df.iloc[best_match_idx]['RESPUESTA']
      




chatbot = ProgrammingChatbot("chat_data.csv")
print("Programming Chatbot initialized. Type 'quit' to exit.")

# Función para mostrar un mensaje en el área de texto
def display_message(message, side):
    message_area.config(state=tk.NORMAL, bg="black")

    message_area.insert(tk.END, f"{message}\n", "right_message")
    message_area.yview(tk.END)
    message_area.config(state=tk.DISABLED, bg="black")


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
    message_area.config(bg="black")
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
        message_area.config(state=tk.NORMAL, bg="black")
        char = message[index]

        # Si contiene ☺, aplica el formato especial
        if "☺" in message:
            formatted_char = char.replace("☺", "")  # Eliminar el símbolo ☺
            message_area.insert(tk.END, formatted_char, "code")
        else:
            message_area.insert(tk.END, char, "left_message")
        
        message_area.config(state=tk.DISABLED, bg="black")
        message_area.yview(tk.END)
        
        # Continuar escribiendo el siguiente carácter
        root.after(20, typing_effect, message, index + 1, callback)
    else:
        # Cuando termina de escribir el mensaje, llama al callback
        if callback:
            callback()
        message_area.config(state=tk.NORMAL, bg="black")
        #message_area.insert(tk.END, "\n")
        message_area.config(state=tk.DISABLED, bg="black")


# Habilitar/deshabilitar botón de enviar
def disable_send_button():
    message_entry.config(state=tk.DISABLED, bg="black")
    send_button.config(state=tk.DISABLED)

def enable_send_button():
    send_button.config(state=tk.NORMAL)
    message_entry.config(state=tk.NORMAL, bg="black")

# Configurar la ventana principal
root = tk.Tk()
root.title("UsatBot")
width, height = 700, 600
x, y = (root.winfo_screenwidth() // 2 - width // 2, root.winfo_screenheight() // 2 - height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.resizable(False, False)

root.configure(bg="black")
logo = tk.PhotoImage(file="images/logo.png") 
root.iconphoto(False, logo)


# Marco principal
frame_main = tk.Frame(root, bg="black")
frame_main.pack(fill="both", expand=True)

# Área de texto
frame_messages = tk.Frame(frame_main, bg="black")
frame_messages.pack(padx=10, pady=10, fill="both", expand=True)
message_area = scrolledtext.ScrolledText(frame_messages, wrap=tk.WORD, width=40, height=20,padx=15, pady=15, bg="black", fg="white", state=tk.DISABLED)
message_area.pack(padx=10, pady=10, fill="both", expand=True)
message_area.tag_configure("red", foreground="red", background="yellow")

# Entrada de texto
frame_input = tk.Frame(frame_main, bg="black")
frame_input.pack(pady=10, fill="x", expand=True)
message_entry = tk.Entry(frame_input, width=30, font=("calibri", 14), bg="black", fg="white")
message_entry.pack(side=tk.LEFT, padx=(50, 10), pady=5, ipady=8, fill="x", expand=True)
message_entry.bind("<Return>", send_message)
message_entry.focus()

# Botón enviar
send_button = tk.Button(frame_input, text="Enviar", command=send_message, font=("calibri", 14), bg="#00BFFF", fg="white", activebackground="#1E90FF")
send_button.pack(side=tk.LEFT, padx=(10, 50), pady=5, ipady=4)

# Configuración de mensajes
message_area.tag_configure("left_message", justify="left", foreground="white", font=("calibri", 14))
message_area.tag_configure("code", justify="left", foreground="cyan", font=("Consolas", 14, "italic"))
message_area.tag_configure("right_message", justify="right", foreground="white", font=("calibri", 14))

# Ejecutar la aplicación
root.mainloop()

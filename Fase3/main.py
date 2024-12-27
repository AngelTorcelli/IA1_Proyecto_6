import tkinter as tk
from idioma_chat import traducir

def saludo():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: ¡Hola! ¿Cómo puedo ayudarte hoy?\n")
    chat_display.config(state=tk.DISABLED)
    
def chistes():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: ¿Por qué los programadores prefieren el osciloscopio? ¡Porque les gustan las señales!\n")
    chat_display.config(state=tk.DISABLED)
    
def datos_curiosos():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: Sabías que el primer bug fue un insecto real que quedó atrapado en un computador?\n")
    chat_display.config(state=tk.DISABLED)
    
def consejos():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: Siempre haz un buen control de versiones para tu código. ¡Nunca sabes cuándo lo necesitarás!\n")
    chat_display.config(state=tk.DISABLED)
    
def herramientas():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: Algunas herramientas útiles son GitHub, VSCode y Postman.\n")
    chat_display.config(state=tk.DISABLED)
    
def conceptos():
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "Bot: Un concepto importante de programación es la encapsulación, que agrupa datos y métodos.\n")
    chat_display.config(state=tk.DISABLED)
    
def enviar_mensaje():
    user_message = message_input.get()
    if user_message:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Tú: {user_message}\nTraduccion: {traducir(user_message)}\n") #importe la función traducir y la usé aqui para probar
        message_input.delete(0, tk.END)
        chat_display.config(state=tk.DISABLED)


def iniciar_app():
    intro_frame.pack_forget()  
    menu_frame.pack(pady=10) 
    chat_frame.pack(pady=10)  


root = tk.Tk()
root.title("UsatBot")
root.geometry("500x600")

intro_frame = tk.Frame(root)
intro_frame.pack(pady=10)
intro_img = tk.PhotoImage(file="images/logo.png")  
intro_label = tk.Label(intro_frame, image=intro_img)
intro_label.pack()
welcome_label = tk.Label(intro_frame, text="¡Bienvenido al UsatBot!", font=("Arial", 16))
welcome_label.pack()


root.after(3000, iniciar_app)  

menu_frame = tk.Frame(root)
menu_frame.pack_forget()  
menu_label = tk.Label(menu_frame, text="Selecciona un tema:", font=("Arial", 14))
menu_label.pack()

buttons = [
    ("Saludos", saludo),
    ("Chistes de programación", chistes),
    ("Datos curiosos de programación", datos_curiosos),
    ("Consejos de programación", consejos),
    ("Herramientas útiles", herramientas),
    ("Conceptos básicos de programación", conceptos)
]

for text, func in buttons:
    button = tk.Button(menu_frame, text=text, width=30, command=func)
    button.pack(pady=5)


chat_frame = tk.Frame(root)
chat_frame.pack_forget()  
chat_display = tk.Text(chat_frame, height=15, width=50, wrap=tk.WORD)
chat_display.pack()
chat_display.config(state=tk.DISABLED)

message_input_frame = tk.Frame(root)
message_input_frame.pack(pady=10)
message_input = tk.Entry(message_input_frame, width=40)
message_input.pack(side=tk.LEFT, padx=5)
message_input.bind("<Return>", lambda event: enviar_mensaje())  # Vincula Enter con enviar_mensaje
send_button = tk.Button(message_input_frame, text="Enviar", command=enviar_mensaje)
send_button.pack(side=tk.LEFT)

root.mainloop()

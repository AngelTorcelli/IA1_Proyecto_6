# Manual de Técnico de USATBOT

*Universidad de San Carlos de Guatemala*  
*Escuela de Ingeniería en Ciencias y Sistemas, Facultad de Ingenieria*  
*Inteligencia Artificial 1, Vacaciones de Diciembre 2024.*  
*Grupo 6*  

| Nombre | Carnet |
| -------- | -------- |
| William Adolfo Mazariegos García    | 202100123     |
| Damaris Julizza Muralles Véliz     | 202100953  |
| Angel David Torcelli Barrios  | 201801169    |

___

## Índice
1. [Introducción](#introducción)
2. [Componentes principales](#componentes)
    1. [Modelo de Inteligencia Artificial](#modelo)
    2. [Generación de datos de entrenamiento](#datos)
    3. [Interfaz gráfica](#interfaz)


## Introducción <a id="introducción"></a>

El proyecto consiste en el desarrollo de un chatbot en español utilizando TensorFlow.js para el modelo de inteligencia artificial. Este chatbot:

- Procesa preguntas en lenguaje natural: Codifica entradas de texto y las compara con un modelo previamente entrenado.
- Responde con frases predefinidas: Basadas en una correspondencia probabilística de las entradas con respuestas entrenadas.
- Interfaz gráfica interactiva: Permite la comunicación con el usuario mediante un diseño amigable.

##  Componentes principales <a id="componentes"></a>
### Modelo de inteligencia artificial <a id="modelo"></a>
El modelo es un perceptrón multicapa (MLP) desarrollado con TensorFlow.js. Este recibe vectores de entrada (codificaciones de palabras clave) y produce salidas categóricas que corresponden a respuestas predefinidas.

Para el presente proyecto se utilizó un modelo secuencial con una capa densa de salida con activación softmax (para obtener probabilidades de las respuestas). La función de pérdida utilizada fue la entropía cruzada categórica para problemas de clasificación multiclase y el optimizador Adam para la actualización de los pesos del modelo. <br>

A continuación, se muestra el código de la definición del modelo:
```javascript
const model = tf.sequential();
model.add(tf.layers.dense({ 
    units: targetData[0].length, 
    inputShape: [keywords.length], 
    activation: 'softmax' 
}));
model.compile({ 
    loss: 'categoricalCrossentropy', 
    optimizer: 'adam', 
    metrics: ['accuracy'] 
});

```
Para el entrenamiento del modelo se utilizó el método fit de TensorFlow.js, el cual recibe tensores de entrada y salida, así como un objeto de configuración con el número de epochs, que consisten en iteraciones completas del conjunto de datos de entrenamiento.
```javascript
async function trainModel() {
    await model.fit(trainingTensor, targetTensor, { epochs: 500 });
}
```

Para el procesamiento de entradas de texto, se utilizó la función encodeInput, que recibe un mensaje y devuelve un tensor de entrada para el modelo.
```javascript	
function encodeInput(input) {
    const vector = Array(keywords.length).fill(0);
    input.toLowerCase().split(" ").forEach(word => {
        if (keywords.includes(word)) {
            vector[keywords.indexOf(word)] = 1;
        }
    });
    return tf.tensor2d([vector]);
}

```

Para la decodificación de las salidas del modelo, se utilizó la función decodeOutput, que recibe un tensor de salida y devuelve la respuesta correspondiente.
```javascript
function decodeOutput(output) {
    const predictions = output.dataSync();
    const maxIndex = predictions.indexOf(Math.max(...predictions));
    if (predictions[maxIndex] < 0.05) {
        return "Lo siento, no entiendo la pregunta.";
    }
    return targetResponses[maxIndex];
}

```
Si la probabilidad más alta es menor a 5%, el chatbot responde que no entiende. De lo contrario, selecciona la respuesta con mayor probabilidad. Esto se hace para evitar respuestas incorrectas o incoherentes.

## Generación de datos de entrenamiento <a id="datos"></a>
Para la generación de datos para entrenar el modelo se utilizó python.
A partir de un archivo de texto (conversaciones.txt), se procesaron líneas de conversación para crear pares de entrada y salida. Las palabras clave se extrajeron y se generaron vectores binarios que representaron las preguntas.

El archivo de texto tiene el siguiente formato:
```
Sujeto A: Hola como estas?
Sujeto B: Hola, estoy bien gracias. ¿Y tu?
Sujeto A: Tambien estoy bien gracias.
Sujeto B: Me alegra escuchar eso.
Sujeto A: Como te llamas?
Sujeto B: Me llamo USATBOT.
```


Para leer el archivo de texto y extraer las conversaciones, se utilizó el siguiente código en Python:
```python
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

```
Como se puede observar en el código, se procesan las líneas del archivo de texto y se extraen las conversaciones. Se generan pares de entrada y salida, donde la entrada es el mensaje anterior y la salida es el mensaje actual. Las respuestas se almacenan en una lista para su uso posterior.

A continuación, se muestra el código de la función que codifica un mensaje en un vector binario:
```python
def encode_message(message, keywords):
    encoding = [1 if word in message.lower().split() else 0 for word in keywords]
    return encoding
```
Cada palabra clave se convierte en un vector binario de 1s y 0s, donde 1 indica que la palabra está presente en el mensaje y 0 indica que no lo está.
<br>
Para la generación de los datos de entrenamiento, se utilizó el siguiente código en Python:
```python
with open("chatbot_data.js", "w", encoding="utf-8") as js_file:
    js_file.write("//Esta variable contiene una lista de las palabras clave (tokens) que se extraen de las conversaciones.\n")
    js_file.write("const keywords = [\n")
    for keyword in keywords:
        js_file.write(f"\t'{keyword}',\n") 
    js_file.write("];\n\n")

```
En el código anterior, se crea un archivo JavaScript con las palabras clave extraídas de las conversaciones. 


## Interfaz gráfica <a id="interfaz"></a>
Para la interfaz gráfica se utilizó HTML, CSS y JavaScript. Se crearon elementos de HTML para mostrar las conversaciones y se implementaron funciones de JavaScript para enviar mensajes y recibir respuestas del chatbot.

A continuación, se muestra el código HTML donde se inserta el chatbot:
```html	
    <div id="chatbot">
        <div id="loading-msg">
            Cargando modelo...
        </div>
        <div id="chat-window">
            <div id="messages"></div>
        </div>
        <div id="input-area">
            <input type="text" id="user-input" class="form-control" placeholder="Escribe tu mensaje aquí..." />
            <button type="button" class="btn btn-primary" id="send-button"><svg xmlns="http://www.w3.org/2000/svg"
                    width="25" height="25" viewBox="0 0 20 20">
                    <path fill="currentColor" d="m0 0l20 10L0 20zm0 8v4l10-2z" />
                </svg></button>
        </div>
    </div>
```

Como se puede observar en el código, se crearon elementos div para mostrar los mensajes y el área de entrada de texto. Se utilizó un botón para enviar los mensajes y se implementaron funciones de JavaScript para manejar los eventos de clic en el botón y presionar la tecla Enter.

## Flujo del sistema <a id="flujo"></a>

1. Procesamiento del entrenamiento:
    1. Primero se debe generar el archivo **chatbot_data.js** con los datos de entrenamiento. Para ello, se debe ejecutar el script de python **conversor.py**. Las onversaciones en el archivo de texto son transformadas en vectores de entrada y salidas esperadas.
    2. El modelo es entrenado cuando el usuario ingresa a la página ejecutando inmediatamente el script.js para asociar patrones de entradas con respuestas predefinidas.

2. Codificación del input:
La entrada del usuario es transformada en un vector binario usando las palabras clave.

3. Predicción:
    1. El modelo secuencial de TensorFlow predice la probabilidad de cada respuesta posible. La respuesta con mayor probabilidad es seleccionada y se verifica que cumpla con un umbral mínimo, de lo contrario, se envía un mensaje de error. 
    2. La respuesta seleccionada es decodificada y mostrada en la interfaz gráfica.

4. Interacción en la interfaz:
    1. El usuario escribe preguntas en un cuadro de texto.
    2. El chatbot responde simulando un efecto de escritura.



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
    1.[Modelo de inteligencia artificial](#modelo)
    2.[Carga del Modelo en el Chatbot Usatbot](#carga)
    3.[Generación de datos de entrenamiento a partir de conversaciones](#generacion)
3. [Modelo de inteligencia artificial](#modelo)
    1.[Uso de TensorFlow.js](#tensorflow)
    2.[Flujo de trabajo del chatbot](#flujo)
    3.[Modularidad del sistema](#modularidad)
    4.[Proceso resumido](#proceso)
4. [Generación de datos de entrenamiento a partir de conversaciones](#generacion)
    1.[Importación de librerías](#librerias)
    2.[Función para generar n-gramas](#ngramas)
    3.[Lectura del archivo de conversaciones](#lectura)
    4.[Validación de balance entre sujetos](#balance)
    5.[Procesamiento del archivo línea por línea](#procesamiento)
    6.[Generación de palabras clave (keywords)](#keywords)
    7.[Codificación de mensajes](#codificacion)
    8.[Generación de datos de entrenamiento y objetivo](#entrenamiento)
    9.[Validación de los datos generados](#validacion)
    10.[Guardado de datos en un archivo JavaScript](#guardado)
    11.[Mensajes de éxito](#exito)

---

## Introducción <a id="introducción"></a>

El proyecto consiste en el desarrollo de un chatbot en español utilizando TensorFlow.js para el modelo de inteligencia artificial. Este chatbot:

- Procesa preguntas en lenguaje natural: Codifica entradas de texto y las compara con un modelo previamente entrenado.
- Responde con frases predefinidas: Basadas en una correspondencia probabilística de las entradas con respuestas entrenadas.
- Interfaz gráfica interactiva: Permite la comunicación con el usuario mediante un diseño amigable.

---

##  Componentes principales <a id="componentes"></a>
### Modelo de inteligencia artificial <a id="modelo"></a>
El modelo es un perceptrón multicapa (MLP) desarrollado con TensorFlow.js. Este recibe vectores de entrada (codificaciones de palabras clave) y produce salidas categóricas que corresponden a respuestas predefinidas.


### Carga del Modelo en el Chatbot Usatbot <a id="carga"></a>

El proceso que permite que el modelo de aprendizaje automático se cargue de inmediato en nuestro chatbot se basa en el uso de **TensorFlow.js** y un flujo bien estructurado entre entrenamiento y ejecución. A continuación, se detallan los pasos y fundamentos de este proceso:

#### **1. Uso de TensorFlow.js** <a id="tensorflow"></a>

**TensorFlow.js** es una biblioteca que nos permite entrenar y ejecutar modelos de aprendizaje automático directamente en el navegador. En el caso de nuestro chatbot, aprovechamos dos de sus capacidades principales:

- **Cargar modelos preentrenados**:  
  Mediante la función `tf.loadLayersModel`, cargamos un modelo previamente entrenado desde dos archivos:
  - `usatbot.json`: contiene la arquitectura y configuración del modelo.
  - `usatbot.weights.bin`: contiene los pesos entrenados del modelo.

- **Ejecución en el cliente**:  
  Una vez cargados estos archivos, el modelo se inicializa completamente en la memoria del navegador del usuario, lo que elimina la necesidad de un servidor externo para realizar predicciones.

#### **2. Flujo de trabajo del chatbot** <a id="flujo"></a>

Nuestro sistema tiene dos etapas claramente diferenciadas: el **entrenamiento del modelo** y la **carga para inferencia**.

##### **2.1. Entrenamiento del modelo**
Utilizamos el archivo `Entrenamiento/script_entrenamiento.js` para realizar el entrenamiento del modelo directamente en el navegador:

1. **Entrenamiento**:  
   El modelo se entrena con los datos proporcionados en las variables `trainingData` y `targetData`. La estructura del modelo y los parámetros de entrenamiento se definen de la siguiente forma:
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
   El entrenamiento se realiza mediante la función `model.fit`, con un número configurable de épocas.

2. **Exportación del modelo**:  
   Una vez completado el entrenamiento, el modelo se guarda en dos archivos:
   - `usatbot.json`: define la arquitectura y la configuración del modelo.
   - `usatbot.weights.bin`: contiene los pesos entrenados del modelo.  
   Esto se logra con la función:
   ```javascript
   await model.save('downloads://usatbot');
   ```
   Al ejecutar esta función, el navegador descarga ambos archivos, que posteriormente deben moverse a la carpeta `/Modelo`.


##### **2.2. Carga y uso del modelo** <a id="carga_modelo"></a>
Una vez entrenado el modelo, usamos el archivo `script.js` para cargarlo y ejecutarlo en el navegador del usuario.

1. **Carga del modelo**:  
   La función `loadModel` se encarga de reconstruir el modelo a partir de los archivos `usatbot.json` y `usatbot.weights.bin` ubicados en la carpeta `/Modelo`. Esto se realiza con el siguiente código:
   ```javascript
   const modelPath = './Modelo/usatbot.json';
   model = await tf.loadLayersModel(modelPath);
   ```
   - `tf.loadLayersModel` carga la arquitectura desde el archivo JSON.
   - Los pesos entrenados se descargan automáticamente desde el archivo BIN asociado.  
   Al finalizar, el modelo está listo para realizar predicciones.

2. **Preprocesamiento y predicciones**:  
   El chatbot utiliza funciones específicas para procesar la entrada del usuario, generar predicciones y presentar una respuesta. Por ejemplo:
   - **Preprocesamiento de entrada**:  
     La función `encodeInput` convierte el texto ingresado por el usuario en un vector de características que el modelo puede interpretar.
   - **Decodificación de salida**:  
     La función `decodeOutput` interpreta las probabilidades generadas por el modelo y selecciona la respuesta más probable.



#### **3. Modularidad del sistema** <a id="modularidad"></a>

Este diseño modular permite que el entrenamiento y la ejecución estén desacoplados, lo que proporciona las siguientes ventajas:

- **Velocidad**: Una vez entrenado, el modelo está disponible de inmediato para su uso sin necesidad de pasos adicionales.
- **Flexibilidad**: Podemos ajustar los datos de entrenamiento y reentrenar el modelo solo cuando sea necesario, sin interrumpir el funcionamiento del chatbot.
- **Ejecución completamente en el cliente**: Todo el procesamiento ocurre en el navegador del usuario, eliminando la necesidad de servidores dedicados para cargar o ejecutar el modelo.


#### **4. Proceso resumido** <a id="proceso"></a>

El flujo de trabajo completo es el siguiente:

1. **Entrenamiento del modelo**:
   - Se utiliza el archivo `Entrenamiento/script_entrenamiento.js`.
   - Al finalizar, el modelo se guarda en los archivos `usatbot.json` y `usatbot.weights.bin`.
   - Estos archivos se mueven a la carpeta `/Modelo`.

2. **Carga del modelo para inferencia**:
   - Se utiliza el archivo `script.js`, que carga el modelo desde `/Modelo` utilizando `tf.loadLayersModel`.
   - El modelo está disponible para realizar predicciones en el navegador del usuario.

Este enfoque garantiza que el chatbot pueda entrenarse y ajustarse con facilidad mientras sigue siendo rápido y eficiente durante su uso en producción.

### **Generación de datos de entrenamiento a partir de conversaciones** <a id="generacion"></a>

El script `conversor.py` procesa un archivo de texto plano con conversaciones estructuradas para generar datos de entrenamiento y objetivos en formato vectorial. Estos datos son utilizados posteriormente para entrenar el modelo de inteligencia artificial.


#### **1. Importación de librerías** <a id="librerias"></a>

El script utiliza las siguientes bibliotecas:

- **re**: Para trabajar con expresiones regulares.
- **itertools.combinations**: Para generar combinaciones de palabras.
- **os**: Para operaciones con el sistema de archivos, como eliminar archivos.
- **contractions**: Para expandir contracciones en el texto, mejorando el procesamiento del lenguaje natural.


#### **2. Función para generar n-gramas**   <a id="ngramas"></a>

```python
def generate_ngrams(words, n):
    return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]
```
Esta función genera n-gramas (secuencias de n palabras consecutivas) a partir de una lista de palabras. Por ejemplo, a partir de las palabras `["hello", "world"]`, genera un bigrama como `["hello world"]`.


#### **3. Lectura del archivo de conversaciones** <a id="lectura"></a>

El archivo `data1.txt` contiene líneas con conversaciones en el formato `Sujeto A: mensaje` y `Sujeto B: respuesta`. Se cargan todas las líneas en una lista para su procesamiento.

```python
with open("data1.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
```


#### **4. Validación de balance entre sujetos** <a id="balance"></a>

Se asegura que el número de mensajes de "Sujeto A" y "Sujeto B" sea igual. Si hay un desbalance, el script muestra un error, elimina cualquier archivo previo generado (`chatbot_data.js`) y finaliza la ejecución.

```python
if sujeto_a_count != sujeto_b_count:
    print(f"Error: Hay un desbalance en las líneas.")
    if os.path.exists("chatbot_data.js"):
        os.remove("chatbot_data.js")
    exit()
```


#### **5. Procesamiento del archivo línea por línea** <a id="procesamiento"></a>

El script utiliza expresiones regulares para separar el usuario (Sujeto A o B) del mensaje:

```python
match = re.match(r"(Sujeto [A-B]): (.+)", line.strip())
```

- **Sujeto A**: Los mensajes se procesan eliminando caracteres especiales y reemplazando contracciones para un formato uniforme.  
- **Sujeto B**: Solo se expanden las contracciones.

Las interacciones entre Sujeto A (preguntas) y Sujeto B (respuestas) se almacenan como pares de conversación para su posterior uso:

```python
conversation_pairs.append((last_message, message))
```

#### **6. Generación de palabras clave (keywords)** <a id="keywords"></a>

El script extrae unigramas (palabras únicas), bigramas, trigramas y más desde las preguntas de "Sujeto A" para generar una lista de palabras clave únicas. Estas se almacenan en un conjunto y se ordenan al final:

```python
keywords = list(sorted(keywords))
```

#### **7. Codificación de mensajes** <a id="codificacion"></a>

La función `encode_message` convierte un mensaje en un vector binario donde cada posición indica la presencia o ausencia de un término de la lista de palabras clave.

```python
def encode_message(message, keywords):
    words = message.lower().split()
    all_ngrams = []
    for i in range(1, n + 1): 
        all_ngrams.extend(generate_ngrams(words, i))
    encoding = [1 if term in all_ngrams else 0 for term in keywords]
    return encoding
```

#### **8. Generación de datos de entrenamiento y objetivo** <a id="entrenamiento"></a>

Para cada par de conversación (pregunta-respuesta):
- La pregunta se codifica usando `encode_message`.
- Se genera un vector objetivo que identifica la respuesta correcta.

```python
target_data[-1][i] = 1  # Marcar la respuesta correcta
```

#### **9. Validación de los datos generados** <a id="validacion"></a>

Antes de continuar, el script valida que el número de entradas de entrenamiento coincida con el número de etiquetas objetivo. Si no coinciden, elimina el archivo generado previamente y finaliza.


#### **10. Guardado de datos en un archivo JavaScript** <a id="guardado"></a>

Finalmente, el script genera el archivo `chatbot_data.js` con las siguientes variables:

1. **Keywords**: Una lista de las palabras clave extraídas.
2. **TrainingData**: Datos de entrenamiento (representaciones vectoriales de las preguntas).
3. **TargetData**: Etiquetas correspondientes a las preguntas.
4. **TargetResponses**: Respuestas reales que el chatbot devolverá.

El archivo se genera de la siguiente manera:

```python
with open("chatbot_data.js", "w", encoding="utf-8") as js_file:
    js_file.write("const keywords = [\n")
    for keyword in keywords:
        js_file.write(f"    '{keyword}',\n")
    js_file.write("];\n\n")
    # Similar para trainingData, targetData y targetResponses
```

#### **11. Mensajes de éxito** <a id="exito"></a>

Si todo el proceso se ejecuta correctamente, el script indica el número de datos generados y confirma la creación del archivo:

```python
print("Archivo chatbot_data.js generado con éxito.")
```



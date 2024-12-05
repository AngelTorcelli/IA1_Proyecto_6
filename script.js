// Definir el modelo de TensorFlow.js
const model = tf.sequential();
model.add(tf.layers.dense({ units: 6, inputShape: [6], activation: 'softmax' })); // Capa de salida tiene 6 clases
model.compile({ loss: 'categoricalCrossentropy', optimizer: 'adam', metrics: ['accuracy'] });

// Datos de entrenamiento: cada fila es una pregunta codificada como un vector de 6 elementos
const trainingData = tf.tensor2d([
    [1, 0, 0, 0, 0, 0], // "hola"
    [0, 1, 0, 0, 0, 0], // "bien"
    [0, 0, 1, 0, 0, 0], // "gracias"
    [0, 0, 0, 1, 0, 0], // "adiós"
    [0, 0, 0, 0, 1, 0], // "ayuda"
    [0, 0, 0, 0, 0, 1], // "nombre"
]);

// Respuestas asociadas: cada fila es una respuesta codificada como un vector de 6 elementos
const targetData = tf.tensor2d([
    [1, 0, 0, 0, 0, 0], // Respuesta 1: "¡Hola! ¿Cómo estás?"
    [0, 1, 0, 0, 0, 0], // Respuesta 2: "Me alegra escuchar eso."
    [0, 0, 1, 0, 0, 0], // Respuesta 3: "Estoy aquí para ayudarte."
    [0, 0, 0, 1, 0, 0], // Respuesta 4: "¡Adiós! Que tengas un buen día."
    [0, 0, 0, 0, 1, 0], // Respuesta 5: "Claro, estoy aquí para ayudarte."
    [0, 0, 0, 0, 0, 1], // Respuesta 6: "Soy un chatbot básico creado con JavaScript nativo. ¿Y tú?"
]);

// Entrenar el modelo
async function trainModel() {
    console.log('Entrenando el modelo...');
    await model.fit(trainingData, targetData, { epochs: 500 });
    console.log('Entrenamiento completado.');
}

// Función para convertir texto a vectores
function encodeInput(input) {
    const keywords = ["hola", "bien", "gracias", "adiós", "ayuda", "nombre"];
    const vector = Array(6).fill(0);
    keywords.forEach((word, index) => {
        if (input.toLowerCase().includes(word)) {
            vector[index] = 1;
        }
    });
    return tf.tensor2d([vector]);
}

// Modificación en decodeOutput para hacer la asignación más robusta
function decodeOutput(output) {
    const responses = [
        "¡Hola! ¿Cómo estás?",       // Respuesta para "hola"
        "Me alegra escuchar eso.",   // Respuesta para "bien"
        "Estoy aquí para ayudarte.", // Respuesta para "gracias"
        "¡Adiós! Que tengas un buen día.", // Respuesta para "adiós"
        "Claro, estoy aquí para ayudarte.", // Respuesta para "ayuda"
        "Soy un chatbot básico creado con JavaScript nativo. ¿Y tú?", // Respuesta para "nombre"
    ];
    const predictions = output.dataSync(); // Extraer las probabilidades como un array
    const maxIndex = predictions.indexOf(Math.max(...predictions)); // Obtener el índice con mayor probabilidad
    return responses[maxIndex];
}


// Procesar la entrada del usuario
async function processInput(input) {
    const encodedInput = encodeInput(input);
    const prediction = model.predict(encodedInput);
    const response = decodeOutput(prediction);
    return response;
}

// Función de efecto máquina de escribir
function typeEffect(element, text, delay = 50) {
    let i = 0;
    return new Promise((resolve) => {
        const interval = setInterval(() => {
            element.textContent += text.charAt(i);
            i++;
            if (i === text.length) {
                clearInterval(interval);
                resolve();
            }
            scrollToBottom();
        }, delay);
    });
}

// Configuración del DOM para el chatbot
document.addEventListener("DOMContentLoaded", async () => {
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const messages = document.getElementById("messages");

    await trainModel(); // Entrenar el modelo al cargar la página

    // Mostrar mensajes en el chat
    function sendMessage(text, sender, typing = false) {
        const message = document.createElement("div");
        message.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        if (!typing) {
            message.textContent = text;
        }
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        return message;
    }

    sendButton.addEventListener("click", async () => {
        const userText = userInput.value.trim();
        if (userText) {
            sendMessage(userText, "user");
            const botMessageElement = sendMessage("", "bot", true); // Espacio para el mensaje del bot
            const botReply = await processInput(userText);
            await typeEffect(botMessageElement, botReply); // Efecto máquina de escribir
            userInput.value = "";
        }
    });

    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendButton.click();
            userInput.value = "";
        }
    });
});


function scrollToBottom() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
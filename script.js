// Definir el modelo de TensorFlow.js
const model = tf.sequential();
model.add(tf.layers.dense({ units: targetData[0].length, inputShape: [keywords.length], activation: 'softmax' })); // Ajuste a targetData
model.compile({ loss: 'categoricalCrossentropy', optimizer: 'adam', metrics: ['accuracy'] });

// Entrenar el modelo con los datos generados
console.log("Tamaño de trainingData:", trainingData.length);
console.log("Tamaño de targetData:", targetData.length);

const trainingTensor = tf.tensor2d(trainingData);
const targetTensor = tf.tensor2d(targetData);

async function trainModel() {
    console.log('Entrenando el modelo...');
    await model.fit(trainingTensor, targetTensor, { epochs: 500 });
    console.log('Entrenamiento completado.');
}

// Función para convertir texto a vectores
function encodeInput(input) {
    const vector = Array(keywords.length).fill(0);
    input.toLowerCase().split(" ").forEach(word => {
        if (keywords.includes(word)) {
            vector[keywords.indexOf(word)] = 1;
        }
    });
    return tf.tensor2d([vector]);
}

// Decodificación de la salida
function decodeOutput(output) {
    const predictions = output.dataSync(); // Extraer probabilidades como un array
    const maxIndex = predictions.indexOf(Math.max(...predictions)); // Índice con mayor probabilidad
    const response = targetResponses[maxIndex]; // Usar targetResponses con el índice correcto
    return response || "Lo siento, no entiendo la pregunta."; // Si no hay respuesta, devolver un mensaje por defecto
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
    if (typeof text !== "string") {
        console.error("Error: Expected a string, but received:", text);
        text = "Lo siento, algo salió mal."; // Mensaje de error si no es una cadena
    }
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


const model = tf.sequential();
model.add(tf.layers.dense({ units: targetData[0].length, inputShape: [keywords.length], activation: 'softmax' })); // Ajuste a targetData
model.compile({ loss: 'categoricalCrossentropy', optimizer: 'adam', metrics: ['accuracy'] });

console.log("Tamaño de trainingData:", trainingData.length);
console.log("Tamaño de targetData:", targetData.length);
if (trainingData.length !== targetData.length) {
    throw new Error("Error: Las longitudes de trainingData y targetData no coinciden. Deteniendo ejecución.");
}

const trainingTensor = tf.tensor2d(trainingData);
const targetTensor = tf.tensor2d(targetData);

async function trainModel() {
    console.log('Entrenando el modelo...');
    document.getElementById("loading-msg").textContent = "Entrenando el modelo... ⌛";
    await model.fit(trainingTensor, targetTensor, { epochs: 500 });
    console.log('Entrenamiento completado.');
    document.getElementById("loading-msg").textContent = "Entrenamiento completado ✔️";
    await model.save('downloads://usatbot');
    console.log('Modelo guardado como archivo descargable.');
}

function encodeInput(input) {
    const vector = Array(keywords.length).fill(0);
    const words = input.toLowerCase().split(" ");
    const bigrams = [];
    
    // Generar bigramas de la entrada
    for (let i = 0; i < words.length - 1; i++) {
        bigrams.push(words[i] + " " + words[i + 1]);
    }
    
    const allTerms = words.concat(bigrams); // Unir unigramas y bigramas
    allTerms.forEach(term => {
        if (keywords.includes(term)) {
            vector[keywords.indexOf(term)] = 1;
        }
    });

    return tf.tensor2d([vector]);
}



function decodeOutput(output) {
    const predictions = output.dataSync(); 
    const maxIndex = predictions.indexOf(Math.max(...predictions));
    console.log("Índice de mayor probabilidad:", maxIndex);
    //console.log("Predicciones:", predictions);

    if (predictions[maxIndex] < 0.05) {
        return "Lo siento, no entiendo la pregunta."; 
    }
    const response = targetResponses[maxIndex]; 
    console.log("Respuesta:", response);
    return response;
}


async function processInput(input) {
    const encodedInput = encodeInput(input);
    const prediction = model.predict(encodedInput);
    const response = decodeOutput(prediction);
    return response;
}


function typeEffect(element, text, delay = 50) {
    if (typeof text !== "string") {
        console.error("Error: Expected a string, but received:", text);
        text = "Lo siento, algo salió mal."; 
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


document.addEventListener("DOMContentLoaded", async () => {
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-button");
    const messages = document.getElementById("messages");

    await trainModel(); 


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
            const botMessageElement = sendMessage("", "bot", true); 
            const botReply = await processInput(userText);
            userInput.value = "";
            await typeEffect(botMessageElement, botReply); 
            
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

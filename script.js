let model;
async function loadModel() {
    const loadingMsg = document.getElementById("loading-msg");
    const modelPath = './Modelo/usatbot.json';

    try {
        loadingMsg.textContent = "Cargando modelo... ⌛";

        model = await tf.loadLayersModel(modelPath);

        loadingMsg.textContent = "Modelo cargado ✅";
        loadingMsg.style.color = "green";

        console.log("Modelo cargado desde la carpeta Modelo.");
    } catch (error) {
        console.error("Error al cargar el modelo:", error);

        loadingMsg.textContent = "Error: Modelo no encontrado ❌";
        loadingMsg.style.color = "red";
        throw new Error("Modelo no cargado.");
    }
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

    userInput.disabled = true;
    sendButton.disabled = true;

    try {
        await loadModel(); // para cargar modelo
        userInput.disabled = false;
        sendButton.disabled = false;
    } catch (error) {
        console.error("No se pudo cargar el modelo:", error);
        return;
    }

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
            let idioma = getLanguage(userText);
            console.log("Idioma detectado:", idioma);

            sendMessage(userText, "user");

            //Se determina si se debe procesar directamente o traducir
            let textoProcesado = userText;
            let botReply = "";
            const botMessageElement = sendMessage("", "bot", true);
            
            if (idioma !== "es") {
                textoProcesado = await traducir(userText,"en","es");                
                textoProcesado = textoProcesado.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                console.log("Traducción:", textoProcesado);                
                //procesa la entrada del usuario y obtiene la respuesta del bot en español, despues se traduce a ingles de nuevo
                botReply = await processInput(textoProcesado);
                const botReplyEs = await traducir(botReply,"es","en");
                //console.log("Respuesta traducida:", botReplyEs);
                userInput.value = "";
                await typeEffect(botMessageElement, botReplyEs);
                return;
            }

            botReply = await processInput(textoProcesado);
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


async function traducir(texto,idiomaActual,idiomaDestino) {
    try {
        const response = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(texto)}&langpair=${idiomaActual}|${idiomaDestino}`);
        const data = await response.json();
        return data.responseData.translatedText;
    } catch (error) {
        resultado.textContent = 'Hubo un error al traducir. Por favor, inténtalo de nuevo.';
        console.error('Error:', error);
        return false
    }
}
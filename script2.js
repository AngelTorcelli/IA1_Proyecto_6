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



setTimeout(function () {
    // Ocultar el mensaje introductorio
    document.getElementById('intro-message').style.display = 'none';

    // Mostrar el chatbot y otras secciones
    document.querySelector('.menu').style.display = 'flex';
    document.querySelector('.content_menu').style.display = 'flex';
}, 3000);



document.addEventListener('DOMContentLoaded', async function () {
    const menuItems = document.querySelectorAll(".menu-item");
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageButton = document.getElementById('sendMessage');

    messageInput.disabled = true;
    sendMessageButton.disabled = true;

    try {
        await loadModel(); 
        messageInput.disabled = false;
        sendMessageButton.disabled = false;
    } catch (error) {
        console.error("No se pudo cargar el modelo:", error);
        return;
    }


    // Definimos las preguntas según el elemento del menú
    const preguntas = {
        "Saludos": "Hola, ¿cómo estás?",
        "Chistes": "Cuéntame un chiste",
        "Datos curiosos": "Cuéntame un dato curioso",
        "Consejos de programación": "Dame un consejo de programación",
        "Herramientas útiles": "Recomiéndame una herramienta útil de programación",
        "Conceptos básicos de programación": "¿Qué es Python?",
    };

    // Asignamos eventos a cada elemento del menú
    menuItems.forEach(item => {
        item.addEventListener("click", function () {
            const texto = item.textContent.trim();
            if (preguntas[texto]) {
                messageInput.value = preguntas[texto];
            }
        });
    });

    // Función para agregar un mensaje al chat
    function addMessage(content, isUser) {
        const message = document.createElement('div');
        message.classList.add(isUser ? 'user-message' : 'ia-message', 'message');
        message.innerHTML = `<p>${content}</p>`;
        messagesContainer.appendChild(message);
        scrollToBottom();
    }
    // Función para simular la escritura de la IA
    async function simulateTyping(response) {
        if (typeof response !== "string") {
            console.error("Error: Expected a string, but received:", response);
            response = "Lo siento, algo salió mal.";
        }
        const iaMessage = document.createElement('div');
        iaMessage.classList.add('ia-message', 'message');
        const p = document.createElement('p');
        iaMessage.appendChild(p);
        messagesContainer.appendChild(iaMessage);
        scrollToBottom();

        let index = 0;
        const interval = setInterval(() => {
            p.textContent += response[index];
            index++;
            if (index === response.length) {
                clearInterval(interval);
                scrollToBottom();
            }
        }, 50); 
    }

    
    const contractionsDict = {
        "i'm": "i am",
        "you're": "you are",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "they're": "they are",
        "i've": "i have",
        "you've": "you have",
        "we've": "we have",
        "they've": "they have",
        "i'd": "i would",
        "you'd": "you would",
        "he'd": "he would",
        "she'd": "she would",
        "we'd": "we would",
        "they'd": "they would",
        "don't": "do not",
        "doesn't": "does not",
        "can't": "cannot",
        "won't": "will not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "hasn't": "has not",
        "haven't": "have not",
        "hadn't": "had not",

    };

    //función para expandir las contracciones en el texto
    function expandContractions(text) {
        // Usamos una expresión regular para buscar todas las contracciones
        return text.replace(/\b(?:i'm|you're|he's|she's|it's|we're|they're|i've|you've|we've|they've|i'd|you'd|he'd|she'd|we'd|they'd|don't|doesn't|can't|won't|isn't|aren't|wasn't|weren't|hasn't|haven't|hadn't)\b/gi, function(match) {            
            return contractionsDict[match.toLowerCase()] || match;
        });
    }


    // Evento para manejar el envío de mensaje
    sendMessageButton.addEventListener('click', async () => {
        const userMessage = messageInput.value.trim();
        if (userMessage.trim() !== '') {
            // Detectar el idioma del texto ingresado
            let idioma = getLanguage(userMessage);
            console.log("Idioma detectado:", idioma);
            // Mostrar el mensaje original del usuario en el chat
            addMessage(userMessage, true); 

            // Determinar si se debe procesar directamente o traducir
            let texto_usuario = userMessage;
            // if (idioma == "es") {
            //     texto_usuario = await traducir(userMessage, "es", "en");
            //     console.log("Texto traducido:", texto_usuario);
            // }
            let botReply = "";
            //const botMessageElement = addMessage("",  true);
            messageInput.value = "";
            if (idioma === "es") {
                textoProcesado = await traducir(userMessage,"es","en");                
                textoProcesado = textoProcesado.toLowerCase().replace(/[?|¿|!|¡]/g, "");
                console.log("Traducción de español a ingles :", textoProcesado);                
                //procesa la entrada del usuario y obtiene la respuesta del bot en español, despues se traduce a ingles de nuevo
                botReply = await processInput(textoProcesado);
                const botReplyEs = await traducir(botReply,"en","es");
                //console.log("Respuesta traducida:", botReplyEs);
                messageInput.value = "";
                await simulateTyping( botReplyEs);
                return;
            }

            textoProcesado = expandContractions(userMessage.toLowerCase());
            console.log("Texto procesado:", textoProcesado.replace(/[?|¿|!|¡]/g, ""));
            //quitar signos de preguntas y exclamaciones
            botReply = await processInput(textoProcesado.replace(/[?|¿|!|¡]/g, ""));
            messageInput.value = "";
            await simulateTyping( botReply);
        }
    });


    messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessageButton.click();
            messageInput.value = "";
        }
    });

    // Función para desplazar al fondo del contenedor de mensajes
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    scrollToBottom(); // Asegúrate de que comienza al fondo si hay mensajes previos
});



async function traducir(texto,idiomaActual,idiomaDestino) {
    try {
        // Primero, sustituimos las palabras 'bug' y 'bugs' con un marcador temporal
        const textoOriginal = texto;
        texto = texto.replace(/\b(bug|bugs)\b/gi, match => `[${match}]`);
        
        const response = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(texto)}&langpair=${idiomaActual}|${idiomaDestino}`);
        const data = await response.json();
        let translatedText = data.responseData.translatedText;

        // Restauramos las palabras 'bug' y 'bugs' a su forma original
        translatedText = translatedText.replace(/\[(bug|bugs)\]/gi, match => match.slice(1, -1));

        return translatedText;
    } catch (error) {
        resultado.textContent = 'Hubo un error al traducir. Por favor, inténtalo de nuevo.';
        console.error('Error:', error);
        return false
    }
}
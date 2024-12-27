const model = tf.sequential();
model.add(tf.layers.dense({ units: targetData[0].length, inputShape: [keywords.length], activation: 'softmax' })); // Ajuste a targetData
model.compile({ loss: 'categoricalCrossentropy', optimizer: 'adam', metrics: ['accuracy'] });

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

document.addEventListener("DOMContentLoaded", async () => {
    await trainModel();
});

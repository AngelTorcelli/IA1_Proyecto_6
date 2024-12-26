import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Descargar los recursos necesarios
nltk.download('punkt_tab')

# Inicializar el stemmer
stemmer = PorterStemmer()

# Leer el archivo .txt
input_filename = 'Pruebas_Fase2/prueba_conversaciones.txt'  # Cambia este nombre por el archivo que quieras procesar
output_filename = 'Pruebas_Fase2/prueba_procesada.txt'  # Archivo donde se guardará el texto procesado

# Abrir el archivo y leer su contenido
with open(input_filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Crear una lista para almacenar el texto procesado
processed_lines = []

# Procesar cada línea
for line in lines:
    if line.startswith("Sujeto A:"):
        # Obtener la oración del Sujeto A y tokenizarla
        sentence = line[9:].strip()  # Eliminar "Sujeto A:" y cualquier espacio adicional
        tokens = word_tokenize(sentence)

        # Filtrar los signos de puntuación y otros caracteres no alfabéticos
        tokens_no_punctuation = [word for word in tokens if word.isalnum()]

        # Aplicar stemming a cada palabra
        stemmed_words = [stemmer.stem(word) for word in tokens_no_punctuation]

        # Unir las palabras stemmeadas y agregar a la lista de líneas procesadas
        processed_line = "Sujeto A: " + ' '.join(stemmed_words)
        processed_lines.append(processed_line + '\n')  # Agregar salto de línea después de Sujeto A
    elif line.startswith("Sujeto B:"):
        # Si es Sujeto B, agregamos la línea tal cual está, asegurándonos de que tenga salto de línea
        processed_lines.append(line)

# Escribir el texto procesado en un nuevo archivo, con cada "Sujeto A" y "Sujeto B" en líneas separadas
with open(output_filename, 'w', encoding='utf-8') as output_file:
    output_file.writelines(processed_lines)

print(f"El texto procesado ha sido guardado en '{output_filename}'")

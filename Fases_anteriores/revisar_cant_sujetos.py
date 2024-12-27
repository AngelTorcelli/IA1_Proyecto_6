import re

# Archivo de entrada
archivo = "conversaciones.txt"

# Leer líneas del archivo
with open(archivo, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Patrón para identificar líneas válidas
patron = r"^(Sujeto A|Sujeto B): .+"

# Verificar alternancia
ultimo_usuario = None
for i, line in enumerate(lines, start=1):
    line = line.strip()
    
    # Validar que la línea tenga el formato correcto
    match = re.match(patron, line)
    if not match:
        print(f"Línea {i} no sigue el formato correcto: {line}")
        continue
    
    # Verificar alternancia entre Sujeto A y Sujeto B
    usuario_actual = match.group(1)
    if usuario_actual == ultimo_usuario:
        print(f"Línea {i} rompe la alternancia: {line}")
    
    ultimo_usuario = usuario_actual

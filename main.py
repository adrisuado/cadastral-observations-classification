
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="./models/mdeberta"
)

texto = "No se encontró al propietario durante la visita"

categorias = ["propiedad", "inmueble", "vivienda", "legal", "administrativo", "otro"]

resultado = classifier(
    texto,
    categorias
)

print(resultado)
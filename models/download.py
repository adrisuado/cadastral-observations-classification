from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

# Nombre del modelo preentrenado que se va a descargar y guardar localmente
MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

# Descargar el tokenizer y el modelo preentrenado
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Guardar el tokenizer y el modelo localmente en la carpeta "models/mdeberta"
tokenizer.save_pretrained("./models/mdeberta")
model.save_pretrained("./models/mdeberta")
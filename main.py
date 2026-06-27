from nlp.ClassificationModel import ClassificationModel
from utils.data_processing import load_data, es_observacion_valida
from utils.db_manager import DBManager
from utils.report import generate_report

# ─────────────────────────────────────────────
# 1. Configuración
# ─────────────────────────────────────────────
MODEL_PATH = "models/mdeberta"
DB_PATH    = "data/catastro.sqlite"
CSV_PATH   = "data/prueba.csv"

# Categorías con descripción ampliada para mejorar la clasificación zero-shot
CLASSES = [
    "Acceso e identificación del predio: problemas para ingresar, dirección no encontrada, portón cerrado, acceso bloqueado, sin número de puerta",
    "Propietario y situación de ocupación: propietario ausente, inquilino, usurpación, proceso judicial, sucesión, apoderado legal",
    "Documentación legal y registral: título incompleto, partida registral, contrato de compraventa, declaratoria de fábrica, inscripción pendiente",
    "Linderos y delimitación del terreno: hitos removidos, superposición con colindante, linderos no coinciden, polígono desplazado, muro divisorio en disputa",
    "Construcciones y estado físico de edificaciones: ampliación sin licencia, construcción en mal estado, adobe deteriorado, obra en curso, altura excedida",
    "Servicios e infraestructura básica: agua potable, alcantarillado, electricidad, gas, pozo séptico, conexión clandestina",
    "Uso actual del predio: vivienda, comercio, industria, agrícola, estacionamiento, baldío, uso mixto, zona de riesgo",
    "Incidencias de levantamiento catastral: error en numeración, coordenadas incorrectas, codificación errada, ficha desactualizada, dato a corregir"
]

# ─────────────────────────────────────────────
# 2. Base de datos
# ─────────────────────────────────────────────
db = DBManager(DB_PATH)
db.create_table()

# ─────────────────────────────────────────────
# 3. Carga e inserción de datos CSV
# ─────────────────────────────────────────────
datos_csv = load_data(CSV_PATH)

# Filtrar observaciones inválidas antes de insertar
datos_validos = [d for d in datos_csv if es_observacion_valida(d.get('observacion', ''))]
descartados   = len(datos_csv) - len(datos_validos)

if descartados > 0:
    print(f"⚠  Se descartaron {descartados} registros con observaciones inválidas.")

db.insert_data(datos_validos)

# ─────────────────────────────────────────────
# 4. Recuperar pendientes de clasificación
# ─────────────────────────────────────────────
sin_clasificar = db.get_unclassified()
print(f"Registros pendientes de clasificación: {len(sin_clasificar)}")

if sin_clasificar:
    ids          = [row[0] for row in sin_clasificar]
    observaciones = [row[1] for row in sin_clasificar]

    # ─────────────────────────────────────────
    # 5. Clasificar con el modelo NLP
    # ─────────────────────────────────────────
    print("Cargando modelo y clasificando…")
    classifier = ClassificationModel(MODEL_PATH)
    classifier.classify(observaciones, CLASSES)

    resultados_ia = classifier.get_results()

    # ─────────────────────────────────────────
    # 6. Persistir resultados en la BD
    # ─────────────────────────────────────────
    for i, res in enumerate(resultados_ia):
        db.update_classification(
            id_predio  = ids[i],
            categoria  = res['label_short'],   # etiqueta limpia sin descripción
            confianza  = round(res['score'], 4)
        )

    print("¡Base de datos actualizada con las clasificaciones!")
    classifier.summary()

    # ─────────────────────────────────────────
    # 7. Generar reporte
    # ─────────────────────────────────────────
    generate_report(db)

# ─────────────────────────────────────────────
# 8. Cerrar conexión
# ─────────────────────────────────────────────
db.close()

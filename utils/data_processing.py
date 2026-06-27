import csv
import re


def load_data(path: str, delimiter: str = ",") -> list[dict]:
    """Lee un CSV y devuelve una lista de dicts con las filas."""
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        data = [row for row in reader]
    return data


def get_column(data: list[dict], colname: str) -> list:
    """Extrae una columna específica de la lista de dicts."""
    if not data:
        raise ValueError("La lista de datos está vacía.")
    if colname not in data[0]:
        raise IndexError(f"La columna '{colname}' no existe.")
    return [row[colname] for row in data]


def es_observacion_valida(texto: str) -> bool:
    """
    Valida que una observación sea procesable por el modelo.
    Descarta textos vacíos, muy cortos o compuestos solo de
    números y caracteres especiales.
    """
    if not texto or not isinstance(texto, str):
        return False

    texto_limpio = texto.strip()

    if len(texto_limpio) < 10:
        return False

    # Rechaza si solo contiene dígitos y caracteres no alfabéticos
    if re.fullmatch(r"[\W_0-9]+", texto_limpio):
        return False

    return True

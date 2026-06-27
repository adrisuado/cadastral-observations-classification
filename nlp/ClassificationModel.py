from transformers import pipeline
from collections import Counter
import torch


# Etiqueta corta (sin descripción) para guardar en la BD de forma legible
def _short_label(label: str) -> str:
    """Extrae solo el nombre de la categoría, antes del primer ':'."""
    return label.split(":")[0].strip()


class ClassificationModel:
    """
    Clasificador zero-shot basado en un modelo Transformers local.

    Parámetros
    ----------
    model_path : str
        Ruta local al modelo descargado (p.ej. 'models/mdeberta').
    threshold : float
        Confianza mínima aceptable. Resultados por debajo se marcan
        como 'Revisión manual requerida'.
    """

    def __init__(self, model_path: str, threshold: float = 0.40):
        dispositivo = 0 if torch.cuda.is_available() else -1

        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_path,
            device=dispositivo
        )

        self.model_path = model_path
        self.threshold  = threshold
        self.results    = None

    # ------------------------------------------------------------------
    def classify(self, textos: list[str], clases: list[str], batch_size: int = 8):
        """
        Clasifica una lista de textos.

        Resultado almacenado en self.results: lista de dicts con:
          - 'sequence'    : texto original
          - 'label_short' : categoría corta (sin descripción)
          - 'label_full'  : categoría completa tal como se pasó al modelo
          - 'score'       : confianza (float 0-1)
          - 'low_conf'    : True si está por debajo del umbral
        """
        raw = self.classifier(textos, clases, batch_size=batch_size)

        # pipeline devuelve dict si es un solo texto
        if isinstance(raw, dict):
            raw = [raw]

        processed = []
        for item in raw:
            best_label = item["labels"][0]
            best_score = item["scores"][0]
            low_conf   = best_score < self.threshold

            processed.append({
                "sequence"    : item["sequence"],
                "label_full"  : best_label,
                "label_short" : _short_label(best_label) if not low_conf
                                else "Revisión manual requerida",
                "score"       : best_score,
                "low_conf"    : low_conf,
            })

        self.results = processed

    # ------------------------------------------------------------------
    def get_results(self) -> list[dict]:
        self._check_results()
        return self.results

    # ------------------------------------------------------------------
    def account_classes(self) -> Counter:
        self._check_results()
        return Counter(r["label_short"] for r in self.results)

    # ------------------------------------------------------------------
    def summary(self):
        counts = self.account_classes()
        total  = len(self.results)
        low    = sum(1 for r in self.results if r["low_conf"])

        print("\n" + "=" * 50)
        print("  RESUMEN DE CLASIFICACIÓN")
        print("=" * 50)
        for label, count in sorted(counts.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            print(f"  {label:<42} {count:>4}  ({pct:5.1f} %)")
        print("-" * 50)
        print(f"  Total clasificados   : {total}")
        print(f"  Confianza baja (<{self.threshold:.0%}): {low}")
        print("=" * 50 + "\n")

    # ------------------------------------------------------------------
    def _check_results(self):
        if self.results is None:
            raise ValueError("Ejecute classify() antes de usar este método.")

    # ------------------------------------------------------------------
    def __str__(self):
        return f"ClassificationModel(model='{self.model_path}', threshold={self.threshold})"

from transformers import pipeline
from collections import Counter

class ClassificationModel:
    def __init__(self, model_path, threshold=0.5):
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_path
        )
        self.results = None
        self.model_path = model_path
        self.threshold = threshold
    

    def classify(self, x, classes):

        results = [
            self.classifier(
                texto,
                classes
            ) for texto in x
        ]

        for result in results:
            labels = result['labels']
            scores = result['scores']

            result['labels'] = labels[0]
            result['scores'] = scores[0]

        self.results = results


    def account_classes(self):
        if self.results is None:
            raise ValueError(
                "Debe ejecutar classify() antes de contar las clases."
            )

        labels = [
            result["labels"]
            for result in self.results
        ]

        counts = Counter(labels)
        return counts


    def summary(self):

        counts = self.account_classes()

        print("=" * 40)
        print("RESUMEN DE CLASIFICACIÓN")
        print("=" * 40)

        for label, count in counts.items():
            print(f"{label:<25}: {count}")

        print("-" * 40)
        print(f"Total registros         : {len(self.results)}")


    def get_results(self):
        if self.results is None:
            raise ValueError(
                "Debe ejecutar classify() antes de obtener los resultados."
            )

        return self.results   
    

    def __str__(self):       
        return f"ModeloClasificacion(model_path={self.model_path})"

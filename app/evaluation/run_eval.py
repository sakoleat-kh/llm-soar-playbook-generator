from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sklearn.metrics import accuracy_score, classification_report
from app.services.classifier import classify_alert

DATASET_PATH = Path("data/labelled_alert.json")
OUTPUT_DIR = Path("data/eval_results")
OUTPUT_FILE = OUTPUT_DIR / "v1_baseline.json"

def load_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    
def evaluate(dataset: list[dict]) -> dict:
    y_true = []
    y_pred = []
    predictions = []

    for i, sample in enumerate(dataset, 1):
        print(f"[{i}/{len(dataset)}] {sample['id']}")
        result = classify_alert(sample["text"])

        y_true.append(sample["technique_id"])
        y_pred.append(result.technique_id)

        predictions.append(
            {
                "id": sample["id"],
                "text": sample["text"],
                "ground_truth": sample["technique_id"],
                "prediction": result.technique_id,
                "perdicted_name": result.technique_name,
                "confidence": result.confidence,
                "correct": sample["technique_id"] == result.technique_id,

            }
        )

    accuracy = accuracy_score(y_true, y_pred)

    report = classification_report(
        y_true,
        y_pred, 
        output_dict=True,
        zero_division=0,
    )

    return {
        "timestamp": datetime.utcnow().isoformat() + "z",
        "samples": len(dataset),
        "accuracy": accuracy,
        "classification_report": report,
        "perdictions": predictions,
    }

def save_results(results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

def print_summary(results: dict) -> None:
    print("\n===============================")
    print("Classifier Evalaution")
    print("=================================")
    print(f"Samples     : {results['samples']}")
    print(f"Accuracy    : {results['accuracy']:.3f}")

    report = results["classification_report"]

    print(
        f"{'Technique':15}"
        f"{'Orrecision':>12}"
        f"{"Recall":>12}"
        f"{'F1':>12}"
        f"{'Support':>10}"
    )

    print("-" * 65)
    for label, metrics in report.items():
        if label in ("accuracy", "macro avg", "weighted avg"):
            continue

        print(
            f"{label:15}"
            f"{metrics['precision']:12.3f}"
            f"{metrics['recall']:12.3f}"
            f"{metrics['f1-score']:12.3f}"
            f"{int(metrics['support']):10d}"
        )

    print("-" * 65)

    macro = report["macro avg"]

    print(
        f"{'Macro Avg':15}"
        f"{macro['precision']:12.3f}"
        f"{macro['recall']:12.3f}"
        f"{macro['f1-score']:12.3f}"
        f"{int(macro['support']):10d}"
    )

    print()

def main() -> None:
    dataset = load_dataset(DATASET_PATH)
    dataset = dataset[:10]
    results = evaluate(dataset)
    save_results(results, OUTPUT_FILE)

    print_summary(results)
    print(f"Results written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

    
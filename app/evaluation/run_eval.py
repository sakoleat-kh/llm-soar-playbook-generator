from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

from sklearn.metrics import accuracy_score, classification_report
from app.services.classifier import classify_alert

from app.evaluation.baselines import (keyword_classifier, random_classifier)

DATASET_PATH = Path("data/labelled_alert.json")
OUTPUT_DIR = Path("data/eval_results")
OUTPUT_FILE = OUTPUT_DIR / "final_classifier.json"

def load_dataset(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
    
def evaluate(dataset: list[dict]) -> dict:
    y_true = []

    random_pred = []
    keyword_pred = []
    llm_pred = []

    predictions = []

    path_counts = {
    "llm": 0,
    "fallback": 0,
    "error": 0,
}

    for i, sample in enumerate(dataset, 1):
        print(f"[{i}/{len(dataset)}] {sample['id']}")

        truth = sample["technique_id"]
        y_true.append(truth)

        # aselines
        rand = random_classifier(sample["text"])
        key = keyword_classifier(sample["text"])

        random_pred.append(rand)
        keyword_pred.append(key)

        # LLM
        result = classify_alert(sample["text"])
        path_counts[result.path] += 1
        if result.technique_id != truth:
            print("\n" + "=" * 70)
            print("MISCLASSIFIED SAMPLE")
            print(f"ID          : {sample['id']}")
            print(f"Expected    : {truth}")
            print(f"Predicted   : {result.technique_id}")
            print(f"Confidence  : {result.confidence:.2f}")
            print("\nAlert:")
            print(sample["text"])
            print("=" * 70 + "\n")


        print("\n----------DEBUG----------")
        print(result)
        print("result.path = ", result.path)
        print("type(result.path) =", type(result.path))
        print("---------------------\n")

        llm_pred.append(result.technique_id)
        
        predictions.append(
            {
                "id": sample["id"],
                "text": sample["text"],
                "ground_truth": sample["technique_id"],
                "llm_prediction": result.technique_id,
                "perdicted_name": result.technique_name,
                "confidence": result.confidence,
                "correct": sample["technique_id"] == result.technique_id,
                "path": result.path,
                "random_prediction": rand,
                "keyword_prediction": key,

            }
        )

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "samples": len(dataset),
        "path_counts": path_counts,
        "comparison": {
            "random": {
                "accuracy": accuracy_score(y_true, random_pred),
                "classification_report": classification_report(
                    y_true,
                    random_pred,
                    output_dict=True,
                    zero_division=0,
                ),
            },
            "keyword": {
                "accuracy": accuracy_score(y_true, keyword_pred),
                "classification_report": classification_report(
                    y_true,
                    keyword_pred,
                    output_dict=True,
                    zero_division=0,
                ),
            },
            "llm": {
                "accuracy": accuracy_score(y_true, llm_pred),
                "classification_report": classification_report(
                    y_true,
                    llm_pred,
                    output_dict=True,
                    zero_division=0,
                ),
            },
        },
        "predictions": predictions,
    }

    return results


def save_results(results: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def find_bad(obj, path="root"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                find_bad(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                find_bad(v, f"{path}[{i}]")
        else:
            try:
                json.dumps(obj)
            except TypeError:
                print(f"{path} -> {type(obj)} -> {repr(obj)}")
    find_bad(results)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

def print_summary(results: dict) -> None:
    print("\n===============================")
    print("Classifier Evalaution")
    print("=================================")

    comparison = results["comparison"]

    print(f"{'System':<15}{'Accuracy':>12}")
    print("-" * 30)
    print(f"{'Random':<15}{comparison['random']['accuracy']:>12.3f}")
    print(f"{'Keywod':<15}{comparison['keyword']['accuracy']:>12.3f}")
    print(f"{'LLM System':<15}{comparison['llm']['accuracy']:>12.3f}")

    print("\nInference Paths")
    print("-----------------")
    print(f"LLM         : {results['path_counts']['llm']}")
    print(f"Fallack     : {results['path_counts']['fallback']}")
    print(f"Error       : {results['path_counts']['error']}")
    
    print("\nLLM Per-Class Metrice")
    print(
        f"{'Technique':15}"
        f"{'Precision':>12}"
        f"{'Recall':>12}"
        f"{'F1':>12}"
        f"{'Support':>10}"
    )

    report = comparison["llm"]["classification_report"]

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

    results = evaluate(dataset)

    save_results(results, OUTPUT_FILE)

    print_summary(results)

    print(f"Results written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

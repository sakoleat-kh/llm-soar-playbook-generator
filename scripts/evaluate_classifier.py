import json

from pathlib import Path
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support)
from app.services.classifier import classify_alert

DATASET = Path("data/labelled_alert.json")
OUTPUT_DIR = Path("data/eval_results")
OUTPUT_FILE = OUTPUT_DIR / "official_test_results.json"


def evaluate(alerts, dataset_name):

    """
    Evaluate the classifier on a dataset.
    """

    true_labels = []
    predicted_labels = []
    predictions = []

    print(f"\n===== {dataset_name.upper()} =====")

    for alert in alerts:
        result = classify_alert(alert["text"])

        predicted = result.technique_id
        expected = alert["technique_id"]

        correct = predicted == expected 

        true_labels.append(expected)
        predicted_labels.append(predicted)  

        predictions.append(
             {
                  "id": alert["id"],
                  "expected": expected ,
                  "predicted": predicted,
                  "correct": correct,
             }
        )

        print(
            f"Alert {alert['id']:>2} | "
            f"Expected: {expected :<10} "
            f"Predicted: {predicted:<10} "
            f"{'✓' if correct else '✗'}"
        )

    accuracy = accuracy_score(true_labels, predicted_labels)

    precision, recall, f1, _= precision_recall_fscore_support(
        true_labels,
        predicted_labels,
        average="weighted",
        zero_division=0,
    )

    print("\n" + "=" * 60)
    print(f"{dataset_name} results")
    print("=" * 60)
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    return {
         "num_alerts": len(alerts),
         "accuracy": accuracy,
         "precision": precision,
         "recall": recall,
         "f1": f1,
         "predictions": predictions,
    }


def main ():

    with open(DATASET, "r", encoding="utf-8") as f:
        alerts = json.load(f)

    train_alerts = alerts[:35]
    test_alerts = alerts[35:]

    print(f"Training alerts : {len(train_alerts)}")
    print(f"Testing alerts  : {len(test_alerts)}")

    train_results = evaluate(train_alerts, "Training")

    test_results = evaluate(test_alerts, "Official Test")

    gap = {
        "accuracy_gap": train_results["accuracy"] - test_results["accuracy"],
        "precision_gap": train_results["precision"] - test_results["precision"],
        "recall_gap": train_results["recall"] - test_results["recall"],
        "f1_gap": train_results["f1"] - test_results["f1"],
    }

    print("\n" + "=" * 60)
    print("TRAIN vs TEST")
    print("=" * 60)
    print(
        f"Accuracy : {train_results['accuracy']:.4f} -> "
        f"{test_results['accuracy']:.4f} "
        f"(Gap {gap['accuracy_gap']:.4f})"
    )

    print(
         f"Precision: {train_results['precision']:.4f} -> "
         f"{test_results['precision']:.4f} "
         f"(Gap {gap['precision_gap']:.4f})"
    )

    print(
         f"Recall   : {train_results['recall']:.4f} -> "
         f"{test_results['recall']:.4f} "
         f"(Gap {gap['recall_gap']:.4f})"
    )

    print(
        f"F1 Score : {train_results['f1']:.4f} -> "
        f"{test_results['f1']:.4f} "
        f"(Gap {gap['f1_gap']:.4f}) "
    )

    OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    results = {
            "dataset": "official_test",
            "train": {
                "num_alerts": train_results["num_alerts"],
                "accuracy": train_results["accuracy"],
                "precision": train_results["precision"],
                "recall": train_results["recall"],
                "f1": train_results["f1"],
            },
            "test": {
                "num_alerts": test_results["num_alerts"],
                "accuracy": test_results["accuracy"],
                "precision": test_results["precision"],
                "recall": test_results["recall"],
                "f1": test_results["f1"]
            },
            "gap": gap,
            "predictions": test_results["predictions"],
        }
    
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            results,
            f,
            indent=4,
        )
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
    
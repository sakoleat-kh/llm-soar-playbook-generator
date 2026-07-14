import json
from collections import Counter
from pathlib import Path

REQUIRED_FIELDS = {
    "id",
    "text",
    "technique_id",
    "technique_name",
}

def main():
    dataset = Path("data/labelled_alert.json")

    with dataset.open("r", encoding="utf-8") as f:
        alerts = json.load(f)

    counts = Counter()
    errors = []

    ids = set()

    for i, alert in enumerate(alerts, start=1):
        missing = REQUIRED_FIELDS - alert.keys()
        if missing:
            errors.append(
                f"Record {i}: missing fields {sorted(missing)}"
            )
            continue
        if not isinstance(alert["id"], int):
            errors.append(f"Record {i}: id must be an integer")

        if alert["id"] in ids:
            errors.append(f"Duplicate id: {alert['id']}")
        ids.add(alert["id"])

        if not str(alert["text"]).strip():
            errors.append(f"Record {i}: empty text")

        if not str(alert["technique_id"]).strip():
            errors.append(f"Record {i}: empty technique_id")

        if not str(alert["technique_name"]).strip():
            errors.append(f"Record {i}: empty technique_name")
        
        counts[alert["technique_id"]] += 1

    print(f"Total alerts: {len(alerts)}")
    print()

    print("Technique counts:")
    for technique, count in sorted(counts.items()):
        print(f" {technique}: {count}")
    
    print()

    if errors:
        print("Validation FAILED")
        print("-----------------")
        for error in errors:
            print(error)
    else:
        print("Validation PASSED")
        print("All records are valid.")

if __name__ == "__main__":
    main()
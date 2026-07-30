import csv

INPUT_FILE = "data/playbook_evaluation/playbook_scores.csv"

completeness = []
technical = []
actionability = []
overall = []

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        completeness.append(float(row["Completeness"]))
        technical.append(float(row["Technical Accuracy"]))
        actionability.append(float(row["Actionability"]))
        overall.append(float(row["Average"]))

print("=" * 50)
print("PLAYBOOK QUALITY AVERAGES")
print("=" * 50)
print(f"Completeness        : {sum(completeness)/len(completeness):.2f}")
print(f"Technical Accuracy  : {sum(technical)/len(technical):.2f}")
print(f"Actionability       : {sum(actionability)/len(actionability):.2f}")
print(f"Overall             : {sum(overall)/len(overall):.2f}")
import json
import time
import statistics
import requests

from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.alert import Alert
from app.models.playbook_db import Playbook

WEBHOOK_URL = "http://127.0.0.1:8000/webhook/alert"

TOTAL_ALERTS = 10
INTERVAL_SECONDS = 30
POLL_INTERVAL = 0.5

def build_test_alert(index: int):

    return {
        "sender": "benchmark@example.com",
        "subject": f"Latency Benchmark #{index}",
        "body_text": (
            f"ALERT NAME: Benchmark Alert {index}\n\n"
            "PowerShell executed with EncodedCommand "
            "from WINWORD.EXE."
        ),
        "severity": 5,
        "source_system": "Latency Benchmark"
    }

def get_db():
    return SessionLocal()

def find_latest_alert(db: Session):

    return (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .first()
    )

def find_playbook(db: Session, alert_id):

    return (
        db.query(Playbook)
        .filter(
            Playbook.alert_id == alert_id
        )
        .first()
    )

def wait_for_classification(alert_id):

    db = get_db()

    start = time.perf_counter()

    while True:
        alert = (
            db.query(Alert)
            .filter(Alert.id == alert_id)
            .first()
        )

        if (
            alert
            and alert.technique_name
        ):
            elapsed = time.perf_counter() - start
            db.close()
            return elapsed

        db.expire_all()
        time.sleep(POLL_INTERVAL)

def wait_for_playbook(alert_id):

    db = get_db()

    start = time.perf_counter()

    while True:

        playbook = (
            db.query(Playbook)
            .filter(
                Playbook.alert_id == alert_id
            )
            .first()
        )

        if playbook:
            elapsed = (
                time.perf_counter()
                - start
            )

            db.close()

            return elapsed

        db.expire_all()
        time.sleep(POLL_INTERVAL)

classification_times = []
playbook_times = []
total_times = []

print("=" * 70)
print("Starting Latency Benchmark")
print("=" * 70)

for i in range(1, TOTAL_ALERTS + 1):

    print(f"\n[{i}/{TOTAL_ALERTS}] Sending alert...")

    payload = build_test_alert(i)

    post_start = time.perf_counter()

    response = requests.post(
        WEBHOOK_URL,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print("Failed:", response.status_code)
        continue

    time.sleep(1)

    db = get_db()

    latest = find_latest_alert(db)

    if latest is None:
        print("Alert not found.")
        db.close()
        continue

    alert_id = latest.id

    db.close()

    print("Alert ID:", alert_id)

    classify_elapsed = wait_for_classification(alert_id)

    playbook_elapsed = wait_for_playbook(alert_id)

    total_elapsed = (
        time.perf_counter()
        - post_start
    )

    classification_times.append(classify_elapsed)

    classification_to_playbook = max(
        0,
        playbook_elapsed - classify_elapsed
    )
    playbook_times.append(
        classification_to_playbook)

    total_times.append(total_elapsed)

    print(
        f"Classification : {classify_elapsed:.2f} sec"
    )

    print(
        f"Classification -> Playbook : "
        f"{classification_to_playbook:.2f} sec"
    )
    print(
        f"Total          : {total_elapsed:.2f} sec"
    )

    if i != TOTAL_ALERTS:
        print(
            f"\nWaiting {INTERVAL_SECONDS} seconds....\n"
        )

        time.sleep(INTERVAL_SECONDS)

print("\n")
print("=" * 70)
print("LATENCY SUMMARY")
print("=" * 70)

print(
    "{:<32}{:>12}".format(
        "Metric",
        "Average (s)"
    )
)

print("-" * 70)

avg_classification = statistics.mean(classification_times)

avg_playbook = statistics.mean(playbook_times)

avg_total = statistics.mean(total_times)

if not classification_times:
    print("\nNo successful benchmark runs.")

print(
    "{:<32}{:>12.2f}".format(
        "POST -> classification",
        avg_classification
    )
)

print(
    "{:<32}{:>12.2f}".format(
        "Classification -> Playbook",
        avg_playbook
    )
)

print(
    "{:<32}{:>12.2f}".format(
        "POST -> Shuffle-importable",
        avg_total
    )
)

print("=" * 70)

print("\nDetailed Results\n")

for i in range(len(classification_times)):

    print(
        f"{i+1:02d}. "
        f"{classification_times[i]:6.2f}s | "
        f"{playbook_times[i]:6.2f}s | "
        f"{total_times[i]:6.2f}s"
    )

print("\nBenchmark Complete.")
import json
import app.services.chroma_service as chroma_service
import app.services.enrichment as enrichment
import app.services.sigma_service as sigma_service
import app.services.shuffle_template as shuffle_template

from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def test_full_pipeline(monkeypatch):

    monkeypatch.setattr(
        "app.services.chroma_service.search_techniques",
        lambda query, n_results=5:[
            {
                "technique_id": "T1566.001",
                "name": "Spearphishing Attachment",
                "document": "Email attachment phishing"

            }
        ],
    )

    monkeypatch.setattr(
        "app.services.sigma_service.get_sigma_rules",
        lambda tid: [
            {
                "title": "Detect Phishing Attachment",
                "raw_url": "https://example.com/rule.yml"
            }
        ],
    )

    monkeypatch.setattr(
        "app.services.enrichment.get_technique_detail",
        lambda tid: {
            "technique_id": tid,
            "name": "Spearphishing Attachment",
            "description": "Dummy description",
            "tactics": ["initial-access"],
            "data_sources": ["Email Gateway"],
            "sub_techniques": [],
        },
    )

    payload = {
        "sender": "soc@example.com",
        "subject": "Phishing Attachment",
        "body_text": (
            "User opend malicious invoice.docm "
            "from attacker@example.com"
        ),
        "severity": 8,
        "source_system": "Email Gateway",
    }

    response = client.post("/webhook/alert", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "received"
    alert_id = body["alert_id"]

    response = client.get(f"/alerts/{alert_id}")
    assert response.status_code == 200
    alert = response.json()
    print(alert)
    raw = json.loads(alert["raw_json"])
    assert raw["subject"] == payload["subject"]

    response = client.get("/alerts")
    assert response.status_code == 200
    alerts = response.json()

    assert any(a["id"] == alert_id for a in alerts)

    results = chroma_service.search_techniques(raw["body_text"])

    assert len(results) > 0
    technique = results[0]
    assert technique["technique_id"] == "T1566.001"

    detail = enrichment.get_technique_detail(
        technique["technique_id"]
    )

    assert detail is not None

    assert detail["name"] == "Spearphishing Attachment"

    rules = sigma_service.get_sigma_rules(
        technique["technique_id"]
    )

    assert len(rules) == 1

    rendered = shuffle_template.render_shuffle_workflow(
        {
            "workflow_name": "Test Workflow",
            "technique_id": "T1566.001",
            "technique_name": "Spearphishing Attachment",
            "alert_description": payload["body_text"],
            "steps": [
                {
                    "step_name": "Notify",
                    "action": "slack",
                    "parameters": {
                        "channel": "#soc"
                    },
                }
            ],
        }
    )
    assert isinstance(rendered, str)

    assert "Test Workflow" in rendered

    assert "T1566.001" in rendered

    assert "Spearphishing Attachment" in rendered



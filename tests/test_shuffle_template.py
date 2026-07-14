from app.services.shuffle_template import render_shuffle_workflow

workflow = render_shuffle_workflow(
    {
        "workflow_name": "Phishing Investigation",
        "technique_id": "T1566.001",
        "technique_name": "Spearphishing Attachment",
        "alert_description": "Suspiccious attachment detected",
        "start_node": "node1",
        "steps": [
            {
                "id": "node1",
                "step_name": "Repeat Alert",
                "action": "repeat_back_to_me",
                "app_version": "1.2.0",
                "x": 450,
                "y": 400,
                "parameters": [
                    {
                    "name": "call",
                    "value": "Investigate phishing email"
                    }
                ]
            }
        ]
    }
)
print(workflow)
from app.services.chroma_service import collection

THREAT_REPORTS = [
    {
        "id": "apt29_t1059",
        "text": (
            "APT29 executed PowerShell commands after compromising victim systems "
            "to run scripts, perform reconnaissance, and download additional "
            "malicious payloads."
        ),
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "group": "APT29",
        "source": "MITRE ATT&CK"
    },

    {
        "id": "fin7_t1566",
        "text": (
            "FIN7 delivered malicious Microsoft Office documents through targeted "
            "phishing emails to gain initial access to victim networks."
        ),
        "technique_id": "T1566.001",
        "technique_name": "Phishing: Spearphishing Attachment",
        "group": "FIN7",
        "source": "MITRE ATT&CK"
    },

    {
        "id": "volt_typhoon_t1078",
        "text": (
            "Volt Typhoon authenticated using legitimate user accounts to blend "
            "into normal activity and maintain access to compromised systems."
        ),
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "group": "Volt Typhoon",
        "source": "MITRE ATT&CK"
    },

    {
        "id": "sandworm_t1021",
        "text": (
            "Sandworm used Remote Desktop Protocol to move laterally between "
            "internal hosts after obtaining valid credentials."
        ),
        "technique_id": "T1021",
        "technique_name": "Remote Services",
        "group": "Sandworm Team",
        "source": "MITRE ATT&CK"
    },

    {
        "id": "lazarus_t1078",
        "text": (
            "Lazarus Group authenticated with compromised user accounts instead "
            "of exploiting software vulnerabilities, allowing their activity to "
            "blend in with legitimate user behavior."
        ),
        "technique_id": "T1078",
        "technique_name": "Valid Accounts",
        "group": "Lazarus Group",
        "source": "MITRE ATT&CK"
    }
]

for report in THREAT_REPORTS:
    collection.add(
        ids=[report["id"]],
        documents=[report["text"]],
        metadatas=[{
            "technique_id": report["technique_id"],
            "name": report["technique_name"],
            "group": report["group"],
            "source": report["source"],
            "type": "threat_report",
        }],
    )

    print("Successfully loaded threat reports into ChromaDB.")
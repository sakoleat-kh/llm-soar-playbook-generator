from app.services.classifier import classify_alert

result = classify_alert(
    "PowerShell executed an encoded command."
)

print(result.model_dump())
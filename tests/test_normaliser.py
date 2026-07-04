from app.routers.webhook import AlertInput
from app.services.normaliser import normalise_alert

def test_login_alert():
    alert = AlertInput(
        sender="test@test.com",
        subject="Suspicious Login Attempt",
        body_text="User login from 192.168.1.10",
        severity=7,
        source_system="SIEM"
    )

    result = normalise_alert(alert)

    assert result.alert_type == "login"
    assert "192.168.1.10" in result.iocs
    assert result.severity_level == "medium"

def test_malware_alert():
    alert = AlertInput(
        sender="test@test.com",
        subject="Malware Detected",
        body_text="Malicious domain badactor.com identified",
        severity=9,
        source_system="EDR"
    )

    result = normalise_alert(alert)

    assert result.alert_type == "malware"
    assert "badactor.com" in result.iocs
    assert result.severity_level == "high"

def test_phishing_alert():
    alert = AlertInput(
        sender="test@test.com",
        subject="Phishing Email Detected",
        body_text="Suspicious sender from fake-bank.com",
        severity=5,
        source_system="Email Gateway"
    )

    result = normalise_alert(alert)

    assert result.alert_type == "phishing"
    assert "fake-bank.com" in result.iocs

def test_unknown_alert():
    alert = AlertInput(
        sender="test@test.com",
        subject="General Security Notice",
        body_text="No IOC found",
        severity=2,
        source_system="SIEM"
    )

    result = normalise_alert(alert)

    assert result.alert_type == "unknown"
    assert result.severity_level == "low"

def test_multiple_iocs():
    alert = AlertInput(
        sender="test@test.com",
        subject="Malware Alert",
        body_text="IPs: 10.0.0.1 and domain evil.com detected",
        severity=8,
        source_system="SOC"
    )

    result = normalise_alert(alert)

    assert "10.0.0.1" in result.iocs
    assert "evil.com" in result.iocs
    assert len(result.iocs) >= 2
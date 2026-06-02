from modules.safety import emergency_findings, risk_level


def test_emergency_findings():
    findings = emergency_findings("Patient has chest pain and shortness of breath.")
    triggers = {item["trigger"] for item in findings}

    assert "chest pain" in triggers
    assert "shortness of breath" in triggers


def test_risk_level_from_abnormalities():
    abnormalities = {
        "hemoglobin": {"status": "LOW"},
        "wbc": {"status": "HIGH"},
    }

    assert risk_level(abnormalities) == "moderate"
    assert risk_level({}, emergency_count=1) == "critical"

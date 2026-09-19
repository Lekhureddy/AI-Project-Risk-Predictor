from risk_copilot.security import redact_pii, run_security_self_checks


def test_redaction_and_security_checks():
    text="Email dev@example.com and token Bearer abcdefghijklmnopqrstuvwxyz123456"
    cleaned=redact_pii(text)
    assert "dev@example.com" not in cleaned
    assert "abcdefghijklmnopqrstuvwxyz123456" not in cleaned
    checks=run_security_self_checks()
    assert checks
    assert all(item["passed"] for item in checks)

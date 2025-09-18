"""Sample run script for the early-warning-alerts prototype."""

from __future__ import annotations

from disease_rules import predict_risks, risk_score
from notifier import send_sms
from weather_api import get_current_weather


def main() -> None:
    # Use a sample location (Bengaluru)
    lat, lon = 12.9716, 77.5946
    weather = get_current_weather(lat, lon)
    print("Weather:", weather)

    risks = predict_risks(weather)
    for r in risks:
        print(f"- {r['disease']}: {r['risk_level']} | {r['reason']} | {r['suggestion']}")

    overall = risk_score(weather)
    print("Overall risk:", overall)

    # Basic assertions akin to unit tests
    assert {"temperature", "humidity", "rainfall_last_24h"}.issubset(set(weather.keys()))
    assert overall in {"Low", "Medium", "High"}
    assert any(r["risk_level"] in {"Medium", "High"} for r in risks), "Expected at least one elevated risk for demo"

    # Simulate SMS
    phone = "+10000000000"
    alert_text = f"Overall risk: {overall}. " + ", ".join(f"{r['disease']}({r['risk_level']})" for r in risks)
    ok = send_sms(phone, alert_text)
    print("SMS sent:", ok)


if __name__ == "__main__":
    main()



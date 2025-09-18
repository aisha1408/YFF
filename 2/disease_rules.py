"""Rule-based crop disease risk prediction.

Exports:
- predict_risks(weather) -> list of risk dicts
- risk_score(weather) -> overall risk level string
"""

from __future__ import annotations

from typing import Any, Dict, List


Risk = Dict[str, str]


def _risk_level_to_score(level: str) -> int:
    mapping = {"Low": 1, "Medium": 2, "High": 3}
    return mapping.get(level, 1)


def _score_to_level(score: float) -> str:
    if score >= 2.5:
        return "High"
    if score >= 1.75:
        return "Medium"
    return "Low"


def predict_risks(weather: Dict[str, Any]) -> List[Risk]:
    """Evaluate simple heuristics and return a list of risks.

    Each item: {disease, risk_level, reason, suggestion}
    """
    t = float(weather.get("temperature", 0.0))
    h = float(weather.get("humidity", 0.0))
    r = float(weather.get("rainfall_last_24h", 0.0))

    risks: List[Risk] = []

    # Powdery Mildew (wheat)
    if h > 70 and 20 < t < 30:
        level = "High"
        reason = f"Humidity {h:.0f}% and temperature {t:.1f}°C favor mildew."
        suggestion = "Scout fields, apply sulfur or triazole fungicide if symptoms appear."
    elif h > 60 and 18 < t < 32:
        level = "Medium"
        reason = f"Warm and humid conditions may favor mildew (H {h:.0f}%, T {t:.1f}°C)."
        suggestion = "Monitor crop canopy; improve airflow and avoid excess nitrogen."
    else:
        level = "Low"
        reason = "Conditions less favorable for mildew."
        suggestion = "Routine monitoring."
    risks.append({"disease": "Powdery Mildew (wheat)", "risk_level": level, "reason": reason, "suggestion": suggestion})

    # Rice Blast
    if r > 20 and 25 < t < 30:
        level = "High"
        reason = f"Heavy rain {r:.1f} mm and warm temps {t:.1f}°C favor blast."
        suggestion = "Ensure balanced nitrogen; consider prophylactic fungicide in hotspots."
    elif r > 5 and 22 < t < 32:
        level = "Medium"
        reason = f"Recent rain {r:.1f} mm with suitable temps may support blast infection."
        suggestion = "Improve drainage and monitor for lesions on leaves and nodes."
    else:
        level = "Low"
        reason = "Insufficient moisture/temperature alignment for blast."
        suggestion = "Routine monitoring."
    risks.append({"disease": "Rice Blast", "risk_level": level, "reason": reason, "suggestion": suggestion})

    # Aphids (general)
    if h > 60 and t < 20:
        level = "High" if t < 15 else "Medium"
        reason = f"Cool (<20°C) and humid (>60%) conditions support aphid buildup. T={t:.1f}°C, H={h:.0f}%."
        suggestion = "Check undersides of leaves; use neem oil or selective insecticide if needed."
    elif h > 50 and t < 22:
        level = "Medium"
        reason = f"Mild temps and moderate humidity can support aphids. T={t:.1f}°C, H={h:.0f}%."
        suggestion = "Encourage natural enemies; avoid broad-spectrum sprays."
    else:
        level = "Low"
        reason = "Conditions less favorable for aphids."
        suggestion = "Routine monitoring."
    risks.append({"disease": "Aphids", "risk_level": level, "reason": reason, "suggestion": suggestion})

    return risks


def risk_score(weather: Dict[str, Any]) -> str:
    """Aggregate risk across diseases into a single level.

    Uses average of numeric scores and converts back to level.
    """
    risks = predict_risks(weather)
    if not risks:
        return "Low"
    avg = sum(_risk_level_to_score(r["risk_level"]) for r in risks) / len(risks)
    return _score_to_level(avg)


def _run_basic_asserts() -> None:
    # High mildew
    w = {"temperature": 25, "humidity": 80, "rainfall_last_24h": 0}
    risks = predict_risks(w)
    assert any(r["disease"].startswith("Powdery Mildew") and r["risk_level"] == "High" for r in risks)

    # High blast
    w = {"temperature": 27, "humidity": 70, "rainfall_last_24h": 30}
    risks = predict_risks(w)
    assert any(r["disease"] == "Rice Blast" and r["risk_level"] == "High" for r in risks)

    # Aphids medium/high
    w = {"temperature": 18, "humidity": 65, "rainfall_last_24h": 2}
    risks = predict_risks(w)
    assert any(r["disease"] == "Aphids" and r["risk_level"] in {"Medium", "High"} for r in risks)


if __name__ == "__main__":
    _run_basic_asserts()
    print("Disease rule asserts passed.")



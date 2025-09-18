"""CLI JSON API for early-warning-alerts.

Usage examples:
  python json_api.py --lat 12.9716 --lon 77.5946 --days 7 --include-outlook --include-historical
  python json_api.py --city Bengaluru --include-outlook
  python json_api.py --city Delhi --feedback "Very helpful" --advisory-export
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict

from disease_rules import predict_risks, risk_score
from weather_api import get_current_weather, get_historical_weather, get_outlook_weather
from config import FEEDBACK_FILE, LABELS_FILE


def load_json_file(path) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def save_feedback(feedback_text: str, weather: Dict[str, Any], overall_risk: str) -> None:
    """Save feedback to JSON file."""
    try:
        data = load_json_file(FEEDBACK_FILE) or []
        data.append({"text": feedback_text, "weather": weather, "overall": overall_risk})
        FEEDBACK_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"Failed to save feedback: {e}")


def generate_advisory_text(overall_risk: str, risks: list) -> str:
    """Generate advisory text for export."""
    lines = [f"Overall Risk: {overall_risk}", ""]
    for r in risks:
        lines.append(f"- {r['disease']}: {r['risk_level']}")
        lines.append(f"  Reason: {r['reason']}")
        lines.append(f"  Suggestion: {r['suggestion']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    p.add_argument("--city", type=str)
    p.add_argument("--days", type=int, default=7, help="Outlook days (default 7)")
    p.add_argument("--include-outlook", action="store_true")
    p.add_argument("--include-historical", action="store_true")
    p.add_argument("--include-feedback", action="store_true")
    p.add_argument("--include-labels", action="store_true")
    p.add_argument("--feedback", type=str, help="Submit feedback text")
    p.add_argument("--advisory-export", action="store_true", help="Export advisory text")
    args = p.parse_args()

    lat = args.lat
    lon = args.lon
    if (lat is None or lon is None) and args.city:
        # Hardcoded city coordinates for demo
        city_coords = {
            "bengaluru": (12.9716, 77.5946),
            "delhi": (28.6139, 77.2090),
            "mumbai": (19.0760, 72.8777),
            "chennai": (13.0827, 80.2707),
            "kolkata": (22.5726, 88.3639),
        }
        city_key = args.city.lower().strip()
        if city_key in city_coords:
            lat, lon = city_coords[city_key]
        else:
            # Default to Bengaluru
            lat, lon = 12.9716, 77.5946

    if lat is None or lon is None:
        raise SystemExit("Provide --lat/--lon or --city")

    weather = get_current_weather(lat, lon)
    risks = predict_risks(weather)
    overall = risk_score(weather)

    result: Dict[str, Any] = {
        "location": {"lat": lat, "lon": lon},
        "weather": weather,
        "overall_risk": overall,
        "risks": risks,
    }

    if args.include_outlook:
        result["outlook"] = get_outlook_weather(lat, lon, days=args.days)
    if args.include_historical:
        result["historical"] = get_historical_weather(lat, lon, days=3)
    if args.include_feedback:
        result["feedback"] = load_json_file(FEEDBACK_FILE) or []
    if args.include_labels:
        result["labels"] = load_json_file(LABELS_FILE) or []

    # Handle feedback submission
    if args.feedback:
        save_feedback(args.feedback, weather, overall)
        result["feedback_submitted"] = True

    # Handle advisory export
    if args.advisory_export:
        advisory_text = generate_advisory_text(overall, risks)
        result["advisory_text"] = advisory_text

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()



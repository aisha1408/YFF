"""Flask web app for Early Warning Alerts."""

from __future__ import annotations

import json
from flask import Flask, render_template, request, jsonify
from disease_rules import predict_risks, risk_score
from weather_api import get_current_weather, get_historical_weather, get_outlook_weather
from config import FEEDBACK_FILE, LABELS_FILE

app = Flask(__name__)


def load_json_file(path):
    """Load JSON data from file."""
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def save_feedback(feedback_text: str, weather: dict, overall_risk: str) -> None:
    """Save feedback to JSON file."""
    try:
        data = load_json_file(FEEDBACK_FILE)
        data.append({"text": feedback_text, "weather": weather, "overall": overall_risk})
        FEEDBACK_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"Failed to save feedback: {e}")


@app.route('/')
def index():
    """Main page with location input."""
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def get_weather():
    """Get weather data and risks for location."""
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    city = data.get('city')
    
    # Handle city lookup
    if city and not lat and not lon:
        city_coords = {
            "bengaluru": (12.9716, 77.5946),
            "delhi": (28.6139, 77.2090),
            "mumbai": (19.0760, 72.8777),
            "chennai": (13.0827, 80.2707),
            "kolkata": (22.5726, 88.3639),
        }
        city_key = city.lower().strip()
        if city_key in city_coords:
            lat, lon = city_coords[city_key]
        else:
            return jsonify({"error": "City not found"}), 400
    
    if not lat or not lon:
        return jsonify({"error": "Location required"}), 400
    
    # Get weather and risks
    weather = get_current_weather(lat, lon)
    risks = predict_risks(weather)
    overall = risk_score(weather)
    
    # Get historical data for comparison
    historical = get_historical_weather(lat, lon, days=2)
    prev_risk = risk_score(historical[-1]) if len(historical) >= 1 else overall
    
    # Get outlook
    outlook = get_outlook_weather(lat, lon, days=7)
    
    return jsonify({
        "location": {"lat": lat, "lon": lon, "city": city},
        "weather": weather,
        "overall_risk": overall,
        "risks": risks,
        "historical": historical,
        "prev_risk": prev_risk,
        "outlook": outlook
    })


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback."""
    data = request.get_json()
    feedback_text = data.get('text')
    weather = data.get('weather')
    overall_risk = data.get('overall_risk')
    
    if feedback_text:
        save_feedback(feedback_text, weather, overall_risk)
        return jsonify({"success": True})
    
    return jsonify({"error": "Feedback text required"}), 400


@app.route('/feedback')
def get_feedback():
    """Get all feedback."""
    feedback = load_json_file(FEEDBACK_FILE)
    return jsonify(feedback)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

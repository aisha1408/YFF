# early-warning-alerts

Weather-driven crop disease early warning prototype (JSON-only). Built for hackathon demos: fetch weather, run simple rules, translate and send alerts via SMS or in-app.

## Architecture

- `json_api.py`: Main CLI interface for all functionality
- `weather_api.py`: Mock weather data generator; returns temp/humidity/rain/description/timestamp
- `disease_rules.py`: Heuristic rules for Powdery Mildew, Rice Blast, Aphids; overall risk
- `notifier.py`: Mock SMS sender and in-app JSON notification store
- `translate_utils.py`: Translation via `googletrans` if available; mock fallback otherwise
- `config.py`: Paths and configuration
- `sample_run.py`: CLI demo with assertions and SMS simulation

## Setup

1) Python 3.10+
2) Create and activate a virtual environment
3) Install deps:
```bash
pip install -r requirements.txt
```
Notes:
- No API keys needed - uses mock weather data based on location.
- SMS is mocked (printed to console) and returns success.
- If `googletrans` fails, translations fall back to suffix tags like `[HI]`, `[KN]`.

## Web Interface (Recommended)

Start the web server:
```bash
python app.py
```

Then open your browser to: http://localhost:5000

Features:
- Beautiful web interface with weather cards and risk visualization
- Location input (city or coordinates)
- Real-time weather and disease risk assessment
- 7-day outlook with color-coded risk levels
- Feedback submission
- Responsive design

## Command Line Interface

For JSON output, use the CLI:
```bash
python json_api.py --city Bengaluru --include-outlook --days 7
python json_api.py --lat 12.9716 --lon 77.5946 --include-outlook --include-historical
python json_api.py --city Delhi --feedback "Very helpful system"
python json_api.py --city Mumbai --advisory-export
```

## CLI Demo

```bash
python sample_run.py
```
This fetches weather for Bengaluru (or mocked if network fails), prints risks, and simulates SMS.

## Acceptance Criteria

- Weather fetched and displayed in the UI
- At least one risk triggers for the given sample weather (Bengaluru)
- SMS function can be toggled and simulated (works with or without Twilio creds)

## SDG Alignment

- SDG 13 (Climate Action): Anticipatory adaptation through weather-driven risk alerts.
- SDG 12 (Responsible Consumption and Production): Reduces unnecessary pesticide use via targeted advisories.
- SDG 9 (Industry, Innovation and Infrastructure): Demonstrates scalable, low-cost digital advisory infrastructure.

## Disclaimer

This is a simplified prototype for hackathon/demo purposes; agronomic decisions require local expert validation.



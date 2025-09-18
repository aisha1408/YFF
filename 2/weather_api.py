"""Mock weather data generator for demo purposes.

No external API calls - generates deterministic mock data based on location.
Returns a dict with: temperature (°C), humidity (%), rainfall_last_24h (mm),
weather_description, wind_speed, timestamp (ISO 8601).
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional, Tuple, List

from config import (
    CACHE_FILE,
    CACHE_TTL_MINUTES,
    SNAPSHOTS_FILE,
    WEATHER_PROVIDER,
)
import json
import time
import random
from datetime import datetime, timedelta


def _generate_mock_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Generate deterministic mock weather based on location."""
    random.seed(int(lat * 1000 + lon))  # Deterministic based on location
    
    # Simulate realistic weather patterns
    base_temp = 25.0 + (lat - 12.0) * 0.5  # Warmer near equator
    temp_variation = random.uniform(-3, 3)
    temp_c = round(base_temp + temp_variation, 1)
    
    humidity = random.randint(60, 85)
    rainfall = random.uniform(0, 25) if random.random() > 0.6 else 0
    wind_speed = random.uniform(1, 8)
    
    descriptions = ["clear sky", "few clouds", "scattered clouds", "broken clouds", "overcast clouds", "light rain", "moderate rain"]
    desc = random.choice(descriptions)
    
    now_iso = dt.datetime.utcnow().isoformat()
    
    return {
        "temperature": temp_c,
        "humidity": humidity,
        "rainfall_last_24h": round(rainfall, 1),
        "weather_description": desc,
        "wind_speed": round(wind_speed, 1),
        "timestamp": now_iso,
    }


def _cache_key(lat: float, lon: float) -> str:
    return f"{WEATHER_PROVIDER}:{round(lat,4)}:{round(lon,4)}"


def _read_cache() -> Dict[str, Any]:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write_cache(data: Dict[str, Any]) -> None:
    CACHE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_cached_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    cache = _read_cache()
    key = _cache_key(lat, lon)
    entry = cache.get(key)
    if not entry:
        return None
    ts = entry.get("ts", 0)
    if time.time() - ts > CACHE_TTL_MINUTES * 60:
        return None
    return entry.get("weather")


def _set_cached_weather(lat: float, lon: float, weather: Dict[str, Any]) -> None:
    cache = _read_cache()
    key = _cache_key(lat, lon)
    cache[key] = {"ts": int(time.time()), "weather": weather}
    _write_cache(cache)


def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Generate mock weather data for demo purposes.
    
    No external API calls - uses deterministic mock data based on location.
    """
    cached = _get_cached_weather(lat, lon)
    if cached:
        return cached

    result = _generate_mock_weather(lat, lon)
    _set_cached_weather(lat, lon, result)
    return result


def get_historical_weather(lat: float, lon: float, days: int = 3) -> List[Dict[str, Any]]:
    """Mock/simple historical using cached snapshots; extend with real provider later."""
    if SNAPSHOTS_FILE.exists():
        try:
            snaps = json.loads(SNAPSHOTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            snaps = []
    else:
        snaps = []
    key = _cache_key(lat, lon)
    hist = [s["weather"] for s in snaps if s.get("key") == key]
    return hist[-days:]


def get_outlook_weather(lat: float, lon: float, days: int = 7) -> List[Dict[str, Any]]:
    """Generate mock 7–14 day outlook using deterministic variation."""
    daily: List[Dict[str, Any]] = []
    base_weather = _generate_mock_weather(lat, lon)
    
    for i in range(days):
        # Add some variation for each day
        random.seed(int(lat * 1000 + lon) + i)
        
        temp_variation = random.uniform(-2, 2)
        hum_variation = random.randint(-10, 10)
        rain_chance = random.random()
        
        day_weather = {
            "temperature": round(base_weather["temperature"] + temp_variation, 1),
            "humidity": max(40, min(95, base_weather["humidity"] + hum_variation)),
            "rainfall_last_24h": round(random.uniform(0, 20) if rain_chance > 0.7 else 0, 1),
            "weather_description": random.choice(["clear sky", "few clouds", "scattered clouds", "broken clouds", "overcast clouds", "light rain"]),
            "wind_speed": round(random.uniform(1, 8), 1),
            "timestamp": (datetime.utcnow() + timedelta(days=i)).isoformat(),
        }
        daily.append(day_weather)
    
    return daily


def save_snapshot(lat: float, lon: float, weather: Dict[str, Any]) -> None:
    entry = {"key": _cache_key(lat, lon), "weather": weather, "ts": int(time.time())}
    if SNAPSHOTS_FILE.exists():
        try:
            snaps = json.loads(SNAPSHOTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            snaps = []
    else:
        snaps = []
    snaps.append(entry)
    SNAPSHOTS_FILE.write_text(json.dumps(snaps, indent=2), encoding="utf-8")



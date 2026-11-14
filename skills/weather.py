import json
import time
from urllib.parse import urlencode
from urllib.request import urlopen

from skills.common import simple_text

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_TRIGGERS = sorted(
    (
        "whats the weather like", "whats the weather", "what is the weather like", "what is the weather",
        "hows the weather", "how is the weather", "tell me the weather", "give me the weather",
        "check the weather", "whats the temperature", "what is the temperature",
        "weather forecast", "weather", "forecast", "temperature",
    ),
    key=len,
    reverse=True,
)

FILLER_WORDS = ("like", "now", "right", "today", "currently", "outside", "here", "please")
CITY_LEAD_WORDS = ("in", "for", "at")
NOT_A_CITY_WORDS = (
    "me", "you", "it", "there", "them", "a", "an", "the", "my", "this", "that",
    "is", "are", "was", "were", "will", "would", "and", "or", "vs", "versus", "than",
)

CACHE_SECONDS = 600
REQUEST_TIMEOUT = 6

WEATHER_CODES = {
    0: "clear sky", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "foggy with frost",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle", 56: "freezing drizzle", 57: "freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain", 66: "freezing rain", 67: "freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light rain showers", 81: "rain showers", 82: "heavy rain showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with heavy hail",
}

FETCH_ERRORS = (OSError, ValueError, KeyError, IndexError, TypeError)

_places = {}
_forecasts = {}


def parse_request(user_input: str) -> tuple[str, int] | None:
    text = simple_text(user_input)

    for trigger in WEATHER_TRIGGERS:
        if text == trigger or text.startswith(trigger + " "):
            rest = text[len(trigger):].split()
            break
    else:
        return None

    tokens = [t for t in rest if t not in FILLER_WORDS]

    day = 0
    if "tomorrow" in tokens:
        day = 1
        tokens.remove("tomorrow")

    if not tokens:
        return "", day

    if tokens[0] not in CITY_LEAD_WORDS:
        return None

    city_tokens = tokens[1:]
    if not 1 <= len(city_tokens) <= 5:
        return None
    if any(t.strip(",") in NOT_A_CITY_WORDS for t in city_tokens):
        return None

    city = " ".join(city_tokens)
    if not all(ch.isalpha() or ch in " -.,'" for ch in city) or not any(ch.isalpha() for ch in city):
        return None

    return city, day


def fetch_json(base_url: str, params: dict) -> dict:
    with urlopen(f"{base_url}?{urlencode(params)}", timeout=REQUEST_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def find_place(city: str) -> tuple[float, float, str] | None:
    key = city.lower()
    if key in _places:
        return _places[key]

    data = fetch_json(GEOCODING_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
    results = data.get("results") or []
    if not results:
        return None

    found = results[0]
    label = ", ".join(part for part in (found["name"], found.get("country")) if part)
    _places[key] = (found["latitude"], found["longitude"], label)
    return _places[key]


def get_forecast(latitude: float, longitude: float, unit: str) -> dict:
    key = (round(latitude, 2), round(longitude, 2), unit)
    cached = _forecasts.get(key)
    if cached and time.time() - cached[0] < CACHE_SECONDS:
        return cached[1]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "auto",
        "forecast_days": 2,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
    }
    if unit == "fahrenheit":
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"

    data = fetch_json(FORECAST_URL, params)
    _forecasts[key] = (time.time(), data)
    return data


def describe(label: str, data: dict, day: int, unit: str) -> str:
    degrees = "°F" if unit == "fahrenheit" else "°C"
    wind_unit = "mph" if unit == "fahrenheit" else "km/h"

    daily = data["daily"]
    high = round(daily["temperature_2m_max"][day])
    low = round(daily["temperature_2m_min"][day])
    rain = daily["precipitation_probability_max"][day]
    rain_text = f", {round(rain)}% chance of rain" if rain is not None else ""

    if day == 1:
        sky = WEATHER_CODES.get(daily["weather_code"][1], "mixed weather")
        return f"{label} tomorrow: {sky}, high {high}{degrees}, low {low}{degrees}{rain_text}."

    now = data["current"]
    sky = WEATHER_CODES.get(now["weather_code"], "mixed weather")
    return (
        f"{label} right now: {round(now['temperature_2m'])}{degrees}, {sky} "
        f"(feels like {round(now['apparent_temperature'])}{degrees}). "
        f"Humidity {round(now['relative_humidity_2m'])}%, wind {round(now['wind_speed_10m'])} {wind_unit}. "
        f"Today: high {high}{degrees}, low {low}{degrees}{rain_text}."
    )


def try_handle_weather(user_input: str, default_city: str = "", unit: str = "celsius") -> str | None:
    request = parse_request(user_input)
    if request is None:
        return None

    city, day = request
    city = city or default_city
    if not city:
        return "Which city? Say 'weather in <city>', or set MILO_CITY in your .env file."

    try:
        place = find_place(city)
        if place is None:
            return f"I couldn't find a place called '{city}'."
        latitude, longitude, label = place
        return describe(label, get_forecast(latitude, longitude, unit), day, unit)
    except FETCH_ERRORS:
        return "I couldn't reach the weather service right now. Please try again in a moment."
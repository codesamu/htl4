#!/usr/bin/env python3

import argparse
import sys
from typing import Any, Dict, Optional

import requests


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def geocode_city(city: str, language: str = "de") -> Optional[Dict[str, Any]]:
	params = {
		"name": city,
		"count": 1,
		"language": language,
	}
	resp = requests.get(GEOCODE_URL, params=params, timeout=10)
	resp.raise_for_status()
	data = resp.json()
	results = data.get("results") or []
	if not results:
		return None
	return results[0]


def get_current_weather(latitude: float, longitude: float, units: str = "metric") -> Dict[str, Any]:
	# Map units to Open-Meteo parameters
	if units == "imperial":
		temp_unit = "fahrenheit"
		wind_unit = "mph"
		precip_unit = "inch"
	else:
		temp_unit = "celsius"
		wind_unit = "kmh"
		precip_unit = "mm"

	params = {
		"latitude": latitude,
		"longitude": longitude,
		"current": ",".join([
			"temperature_2m",
			"relative_humidity_2m",
			"apparent_temperature",
			"weather_code",
			"wind_speed_10m",
			"wind_direction_10m",
		]),
		"temperature_unit": temp_unit,
		"wind_speed_unit": wind_unit,
		"precipitation_unit": precip_unit,
	}
	resp = requests.get(FORECAST_URL, params=params, timeout=10)
	resp.raise_for_status()
	return resp.json()


def describe_weather_code(code: Optional[int]) -> str:
	# Minimal mapping for common codes per Open-Meteo WMO codes
	mapping = {
		0: "Klar",
		1: "Überwiegend klar",
		2: "Teilweise bewölkt",
		3: "Bedeckt",
		45: "Nebel",
		48: "Reifnebel",
		51: "Niesel (leicht)",
		53: "Niesel (moderat)",
		55: "Niesel (stark)",
		61: "Regen (leicht)",
		63: "Regen (moderat)",
		65: "Regen (stark)",
		71: "Schnee (leicht)",
		73: "Schnee (moderat)",
		75: "Schnee (stark)",
		80: "Regenschauer (leicht)",
		81: "Regenschauer (moderat)",
		82: "Regenschauer (heftig)",
		95: "Gewitter",
		96: "Gewitter mit leichtem Hagel",
		99: "Gewitter mit starkem Hagel",
	}
	return mapping.get(code if code is not None else -1, f"Code {code}")


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Aktuelles Wetter für eine Stadt (Open-Meteo, keine API-Keys)")
	parser.add_argument("--city", required=True, help="Stadtname, z.B. 'Innsbruck'")
	parser.add_argument("--units", choices=["metric", "imperial"], default="metric", help="Einheiten: metric (°C, km/h) oder imperial (°F, mph)")
	parser.add_argument("--language", default="de", help="Sprachcode für Geocoding, z.B. de, en")
	parser.add_argument("--verbose", action="store_true", help="Zeige detaillierte Fehlerausgaben")
	return parser


def main(argv: list[str]) -> int:
	parser = build_parser()
	args = parser.parse_args(argv)

	try:
		geo = geocode_city(args.city, language=args.language)
		if not geo:
			print({"error": f"Keine Treffer für Stadt '{args.city}'"}, file=sys.stderr)
			return 2

		lat = float(geo["latitude"])  # type: ignore[index]
		lon = float(geo["longitude"])  # type: ignore[index]
		place = geo.get("name")
		country = geo.get("country")

		data = get_current_weather(lat, lon, units=args.units)
		current = data.get("current") or {}

		temp = current.get("temperature_2m")
		hum = current.get("relative_humidity_2m")
		apparent = current.get("apparent_temperature")
		code = current.get("weather_code")
		wind = current.get("wind_speed_10m")
		wdir = current.get("wind_direction_10m")

		unit_temp = data.get("current_units", {}).get("temperature_2m", "")
		unit_wind = data.get("current_units", {}).get("wind_speed_10m", "")

		print({
			"location": f"{place}, {country}",
			"temperature": f"{temp} {unit_temp}",
			"apparent_temperature": f"{apparent} {unit_temp}",
			"relative_humidity": f"{hum} %",
			"wind": f"{wind} {unit_wind}",
			"wind_direction_deg": wdir,
			"conditions": describe_weather_code(code),
		})
		return 0
	except requests.HTTPError as exc:
		resp = exc.response
		if args.verbose and resp is not None:
			print({
				"error": "HTTPError",
				"status_code": resp.status_code,
				"url": resp.url,
				"body": resp.text,
			}, file=sys.stderr)
		else:
			print({"error": str(exc)}, file=sys.stderr)
		return 1
	except requests.RequestException as exc:
		print({"error": str(exc)}, file=sys.stderr)
		return 1


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:])) 
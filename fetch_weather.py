import argparse
import dataclasses
import json
import logging
import os
import pathlib
import sys

import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Location:
    lat: float
    lon: float
    name: str


def get_weather_data(api_key, location, exclude=None, units=None, lang=None):
    base_url = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "units": units,
        "lang": lang,
        "exclude": exclude,
        "lat": location.lat,
        "lon": location.lon,
        "appid": api_key,
    }

    for param in ["exclude", "units", "lang"]:
        if params[param] is None:
            params.pop(param)

    logger.debug(f"API Request URL: {base_url}")
    logger.debug(f"API Request Params: {params}")

    request_object = requests.Request("GET", base_url, params=params)
    prepared_request = request_object.prepare()
    logger.debug(f"Full Request Object: {prepared_request}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error: {response.status_code}, {response.text}")
        return f"Error: {response.status_code}, {response.text}"


def fetch_and_save_weather_data(location: Location) -> None:
    parser = argparse.ArgumentParser(
        description="Fetch weather data from OpenWeatherMap API."
    )
    parser.add_argument(
        "--output", default="data.json", help="Output file path (default: data.json)"
    )

    args = parser.parse_args()

    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

    if api_key is None:
        logger.error(
            "Error: OpenWeatherMap API key not found in environment variables."
        )
        sys.exit(1)

    result = get_weather_data(api_key, location)
    output_path = args.output

    y = json.dumps(result, indent=2)
    pathlib.Path(output_path).write_text(y)


if __name__ == "__main__":
    location = Location(lat=47.608, lon=-122.3352, name="Seattle")
    fetch_and_save_weather_data(location)

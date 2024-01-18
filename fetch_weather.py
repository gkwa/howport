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


# https://openweathermap.org/api/one-call-3#history_daily_aggregation
def fetch_daily_summary(api_key, location, date, tz=None):
    base_url = "https://api.openweathermap.org/data/3.0/onecall/day_summary"

    params = {
        "lat": location.lat,
        "lon": location.lon,
        "date": date,
        "appid": api_key,
    }

    if tz:
        params["tz"] = tz

    logger.debug(f"API Request URL: {base_url}")
    logger.debug(f"API Request Params: {params}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error: {response.status_code}, {response.text}")
        return f"Error: {response.status_code}, {response.text}"


def fetch_and_save_daily_summary_for_date_range(
    api_key, location, date_range, tz, output_path
):
    for date in date_range:
        date_output_path = f"{output_path}-{date}.json"

        if pathlib.Path(date_output_path).exists():
            logger.info(
                f"Skipping API call for {date}, file already exists: {date_output_path}"
            )
            continue

        result = fetch_daily_summary(api_key, location, date, tz)

        y = json.dumps(result, indent=2)
        pathlib.Path(date_output_path).write_text(y)


# https://openweathermap.org/api/one-call-3#history
def fetch_weather_data_for_timestamp(api_key, location, timestamp):
    base_url = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

    params = {
        "lat": location.lat,
        "lon": location.lon,
        "dt": timestamp,
        "appid": api_key,
    }

    logger.debug(f"API Request URL: {base_url}")
    logger.debug(f"API Request Params: {params}")

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error: {response.status_code}, {response.text}")
        return f"Error: {response.status_code}, {response.text}"


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


def parse_command_line_args():
    parser = argparse.ArgumentParser(
        description="Fetch weather data from OpenWeatherMap API."
    )
    parser.add_argument(
        "--output", default="data.json", help="Output file path (default: data.json)"
    )
    parser.add_argument(
        "--timestamp", type=int, help="Timestamp for fetching historical weather data"
    )
    parser.add_argument(
        "--date", help="Date for fetching daily summary data (YYYY-MM-DD format)"
    )
    parser.add_argument(
        "--tz", help="Timezone in the ±XX:XX format for daily summary API call"
    )

    return parser.parse_args()


def fetch_and_save_weather_data(location: Location, date_range=None) -> None:
    args = parse_command_line_args()

    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

    if api_key is None:
        logger.error(
            "Error: OpenWeatherMap API key not found in environment variables."
        )
        sys.exit(1)

    if args.timestamp:
        result = fetch_weather_data_for_timestamp(api_key, location, args.timestamp)
    elif args.date:
        result = fetch_daily_summary(api_key, location, args.date, args.tz)
        output_path = args.output
        y = json.dumps(result, indent=2)
        pathlib.Path(output_path).write_text(y)
    elif date_range:
        fetch_and_save_daily_summary_for_date_range(
            api_key, location, date_range, args.tz, args.output
        )
    else:
        result = get_weather_data(api_key, location)

    output_path = args.output

    y = json.dumps(result, indent=2)
    pathlib.Path(output_path).write_text(y)


if __name__ == "__main__":
    location = Location(lat=47.608, lon=-122.3352, name="Seattle")
    fetch_and_save_weather_data(location)

import argparse
import datetime
import json


def kelvin_to_celsius(kelvin_temp):
    # Formula: K - 273.15
    celsius_temp = kelvin_temp - 273.15
    return celsius_temp


def kelvin_to_fahrenheit(kelvin_temp):
    # Formula: (K - 273.15) * 9/5 + 32
    fahrenheit_temp = (kelvin_temp - 273.15) * 9 / 5 + 32
    return fahrenheit_temp


def extract_hourly_temp(data):
    hourly_temps = []

    for hour_data in data.get("hourly", []):
        temp_info = {
            "epoch": hour_data.get("dt"),
            "timestamp": datetime.datetime.utcfromtimestamp(hour_data.get("dt")),
            "temp_kelvin": hour_data.get("temp"),
            "temp_fahrenheit": kelvin_to_fahrenheit(hour_data.get("temp")),
            "temp_celsius": kelvin_to_celsius(hour_data.get("temp")),
        }
        hourly_temps.append(temp_info)

    return hourly_temps


def main():
    parser = argparse.ArgumentParser(description="Transform weather data.")
    parser.add_argument(
        "--output",
        default="transform.jsonl",
        help="Output file path (default: transform.jsonl)",
    )

    args = parser.parse_args()

    with open("data.json", "r") as json_file:
        data = json.load(json_file)

    hourly_temps = extract_hourly_temp(data)

    with open(args.output, "w") as jsonl_file:
        for temp_info in hourly_temps:
            jsonl_file.write(json.dumps(temp_info, default=str) + "\n")


if __name__ == "__main__":
    main()

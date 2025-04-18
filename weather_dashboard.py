import argparse

import matplotlib.pyplot as plt
import pandas as pd
import requests


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Fetch and analyze weather data.")
    parser.add_argument(
        "--latitude",
        type=float,
        required=True,
        help="Latitude of the location.",
    )
    parser.add_argument(
        "--longitude",
        type=float,
        required=True,
        help="Longitude of the location.",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD).",
    )
    return parser.parse_args()


def fetch_weather_data(latitude, longitude, start_date, end_date):
    """Fetch weather data from the Open-Meteo API.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).

    Returns:
        list: List of daily weather data.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "windspeed_10m_max",
        ],
        "timezone": "auto",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")

    data = response.json()
    return data["daily"]


def process_data(weather_data):
    """Process the weather data and calculate average temperature, wind speed.

    Args:
        weather_data (list): List of daily weather data.

    Returns:
        pd.DataFrame: DataFrame containing the processed weather data.
    """
    df = pd.DataFrame(weather_data)
    df["date"] = pd.to_datetime(df["time"])
    df.set_index("date", inplace=True)
    df.drop(columns=["time"], inplace=True)
    df["temperature_average"] = (
        df["temperature_2m_max"] + df["temperature_2m_min"]
    ) / 2
    return df


def print_weather_stats(df):
    """Print weather statistics such as average temperature, max/min temperature, and max wind speed."""
    avg_temp = df["temperature_average"].mean()
    max_temp = df["temperature_2m_max"].max()
    min_temp = df["temperature_2m_min"].min()
    max_windspeed = df["windspeed_10m_max"].max()

    print("Weather Data Summary:")
    print("----------------------")
    print(f"Date Range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Average Temperature (°C): {avg_temp:.2f}")
    print(f"Max Temperature (°C): {max_temp:.2f}")
    print(f"Min Temperature (°C): {min_temp:.2f}")
    print(f"Max Windspeed (m/s): {max_windspeed:.2f}")
    print()


def plot_graphs(df):
    """Plot graphs."""
    # Plot Average Temperature Over Time
    plt.figure(figsize=(10, 5))

    plt.subplot(3, 1, 1)
    plt.plot(
        df.index,
        df["temperature_average"],
        marker="o",
        linestyle="-",
        color="red",
        label="Average Temperature",
    )
    plt.title("Average Temperature Over Time")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot Max Temperature Over Time
    plt.subplot(3, 1, 2)
    plt.plot(
        df.index,
        df["temperature_2m_max"],
        marker="o",
        linestyle="-",
        color="orange",
        label="Max Temperature",
    )
    plt.title("Max Temperature Over Time")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Plot Min Temperature Over Time
    plt.subplot(3, 1, 3)
    plt.plot(
        df.index,
        df["temperature_2m_min"],
        marker="o",
        linestyle="-",
        color="blue",
        label="Min Temperature",
    )
    plt.title("Min Temperature Over Time")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Adjust layout for spacing between graphs
    plt.subplots_adjust(hspace=0.4)

    # Save graph to a file instead of showing it interactively
    plt.tight_layout()
    plt.savefig("weather_dashboard_plot.png")  # Save as PNG image
    print("Graph saved as weather_dashboard_plot.png")

    # Optionally, close the plot to free up resources
    plt.close()


def main():
    """Main function to orchestrate the weather data analysis process."""
    args = parse_arguments()
    weather_data = fetch_weather_data(
        args.latitude, args.longitude, args.start_date, args.end_date
    )
    df = process_data(weather_data)
    print_weather_stats(df)
    plot_graphs(df)


if __name__ == "__main__":
    main()

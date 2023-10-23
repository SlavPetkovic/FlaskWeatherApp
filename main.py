
# Import Dependencies
from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
import pytz

app = Flask(__name__)

# Load configuration from JSON file
config_file_path = 'parameters/config.json'
with open(config_file_path) as config_file:
    config_data = json.load(config_file)

API_KEY = config_data.get("WeatherAPI")

# Function to get the user's location based on IP address
def get_user_location(city=None):
    # If a city is provided, use it as the location
    if city:
        return city
    try:
        # Attempt to retrieve the user's location based on their IP address
        response = requests.get("https://ipinfo.io")
        data = response.json()
        return data.get("city")
    except requests.RequestException as e:
        print(f"Error getting location: {e}")
        return None

def get_weather_data(city, api_key):
    # Retrieve weather data for a specified city using the OpenWeatherMap API
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&APPID={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def convert_timestamp_to_datetime(timestamp, timezone):
    # Convert a Unix timestamp to a human-readable datetime in a specified timezone
    return datetime.fromtimestamp(timestamp, tz=pytz.utc).astimezone(timezone).strftime('%Y-%m-%d %H:%M')

@app.route('/')
def index():
    user_city = request.args.get('city')

    # If user doesn't specify a city, attempt to get their location based on IP
    if not user_city:
        user_city = get_user_location()

    if user_city:
        data = get_weather_data(user_city, API_KEY)

        if data:
            main_data = data.get('main')
            weather_data = data.get('weather')[0]
            sys_data = data.get('sys')

            # Extract weather information
            temperature = main_data.get('temp')
            temperature_min = main_data.get('temp_min')
            temperature_max = main_data.get('temp_max')
            feels_like = main_data.get('feels_like')
            pressure = main_data.get('pressure')
            humidity = main_data.get('humidity')
            description = weather_data.get('description')

            # Convert sunrise and sunset timestamps to datetime objects
            sunrise_raw = sys_data.get('sunrise')
            sunset_raw = sys_data.get('sunset')

            city = data.get('name')

            # Determine the timezone for the city based on its coordinates
            city_timezone = pytz.timezone(pytz.country_timezones[sys_data['country']][0])

            # Get the current date and time with the city's timezone offset
            current_date = datetime.now(city_timezone).strftime("%Y-%m-%d")
            current_time = datetime.now(city_timezone).strftime("%I:%M %p")

            def convert_timestamp_to_time(timestamp, timezone):
                # Convert a Unix timestamp to a human-readable time in a specified timezone
                return datetime.fromtimestamp(timestamp, tz=pytz.utc).astimezone(timezone).strftime('%I:%M %p')

            # Convert sunrise and sunset timestamps to human-readable times in the city's timezone
            sunrise = convert_timestamp_to_time(sunrise_raw, city_timezone)
            sunset =  convert_timestamp_to_time(sunset_raw, city_timezone)

            return render_template('index.html',
                                   city=city,
                                   temperature=temperature,
                                   description=description,
                                   humidity=humidity,
                                   pressure=pressure,
                                   current_date = current_date,
                                   current_time = current_time,
                                   sunset = sunset,
                                   sunrise = sunrise)
        else:
            return "Error while fetching weather data"
    else:
        return "Error getting user location."

if __name__ == "__main__":
    app.run(debug=True)

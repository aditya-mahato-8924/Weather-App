from flask import Flask, request, render_template

# load the form
from forms import SearchForm

# import json to load JSON data to a python dictionary
import json

# urllib.request to make request to api 
import urllib.request

# for generating secret key
import secrets

# for fetching latitude and longitude of requested place
from geopy.geocoders import Nominatim

# for fetching country name based on country code
import pycountry

# for converting UNIX time to datetime object in order to display sunrise and sunset time
from datetime import datetime, timedelta, timezone

# for fetching api key in production
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route("/", methods=["GET", "POST"])
def home():
    form = SearchForm()
    weather_data, error = None, None

    if request.method == "POST":
        place = form.input_city.data.strip()
        print(place)

        list_of_data = fetch_weather_data(place)

        if list_of_data != "Requested Place data not found":
            sunrise_unix = list_of_data['sys']['sunrise']
            sunset_unix = list_of_data['sys']['sunset']
            timezone_offset = list_of_data['timezone']

            times = extract_sunrise_sunset_time(sunrise_unix, sunset_unix, timezone_offset)

            weather_data = {
                "Country": pycountry.countries.get(alpha_2 = list_of_data['sys']['country']).name,
                "Coordinate": str(list_of_data['coord']['lat']) + " " + str(list_of_data['coord']['lon']),
                "Description": str(list_of_data['weather'][0]['description']).title(),
                "Temperature": str(round(list_of_data['main']['temp'] - 273.15, 2)) + "\u00B0C",
                "Pressure": str(list_of_data['main']['pressure']) + "hPa",
                "Humidity": str(list_of_data['main']['humidity']) + "%",
                "Visibility": str(float(list_of_data['visibility']) / 1000) + "Km",
                "Wind Speed": str(list_of_data['wind']['speed']) + "m/s",
                "Wind Direction": str(list_of_data['wind']['deg']) + "\u00B0",
                "Sunrise": times[0],
                "Sunset": times[1],
                "Timezone" : str(find_timezone(list_of_data['timezone']))
            }
        else:
            error = list_of_data

    return render_template("index.html", title="Weather App", form=form, weather_data=weather_data, error=error or None)

def fetch_weather_data(place_name):
    api = os.getenv("API_KEY")
    lat, lon = fetch_lat_lon(place_name)
    try: 
        source = urllib.request.urlopen(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api}').read()
        data = json.loads(source)
        return data
    except Exception as e:
        return "Requested Place data not found"

def fetch_lat_lon(place_name):
    geolocator = Nominatim(user_agent="my_geopy_app")
    location = geolocator.geocode(place_name)

    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None


def find_timezone(timezone_offset):
    hours = abs(timezone_offset) // 3600
    minutes = (abs(timezone_offset) % 3600) // 60

    if timezone_offset < 0:
        hours = -hours
        minutes = -minutes

    print(timezone(timedelta(hours=hours, minutes=minutes)))
    return timezone(timedelta(hours=hours, minutes=minutes))

def extract_sunrise_sunset_time(sunrise_unix, sunset_unix, timezone_offset):
    # convert into datetime object
    sunrise_time = datetime.fromtimestamp(sunrise_unix, tz=find_timezone(timezone_offset))
    sunset_time = datetime.fromtimestamp(sunset_unix, tz=find_timezone(timezone_offset))

    # convert into string
    sunrise_str = datetime.strftime(sunrise_time, "%I:%M %p")
    sunset_str = datetime.strftime(sunset_time, "%I:%M %p")

    return sunrise_str, sunset_str


if __name__ == "__main__":
    app.run(debug=True)
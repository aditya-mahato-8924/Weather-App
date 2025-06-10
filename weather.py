from flask import Flask, request, url_for, render_template

# load the form
from forms import SearchForm

# import json to load JSON data to a python dictionary
import json

# urllib.request to make request to api 
import urllib.request

# for generating secret key
import secrets

# for converting country code to actual name
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
    weather_data = None
    error = "city not found"
    status = True

    if request.method == "POST":
        city = form.input_city.data.strip().replace(" ", '%20')
        print(city)

        status, list_of_data = is_valid_city(city)

        if status:
            sunrise_unix = list_of_data['sys']['sunrise']
            sunset_unix = list_of_data['sys']['sunset']
            timezone_offset = list_of_data['timezone']

            times = extract_sunrise_sunset_time(sunrise_unix, sunset_unix, timezone_offset)

            weather_data = {
                "Country": pycountry.countries.get(alpha_2 = list_of_data['sys']['country']).name,
                "Coordinate": str(list_of_data['coord']['lon']) + " " + str(list_of_data['coord']['lat']),
                "Temperature": str(round(list_of_data['main']['temp'] - 273.15, 2)) + "\u00B0C",
                "Pressure": str(list_of_data['main']['pressure']) + "hPa",
                "Humidity": str(list_of_data['main']['humidity']) + "%",
                "Sunrise": times[0],
                "Sunset": times[1],
                "Timezone" : str(find_timezone(list_of_data['timezone']))
            }

            print(weather_data)


    return render_template("index.html", title="Weather App", form=form, weather_data=weather_data, error=error if not status else None)

def is_valid_city(city):
    api = os.getenv("API_KEY")
    if not (is_country(city) or is_country_code(city)):
        try: 
            source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' + city + '&appid=' + api).read()

            data = json.loads(source)

            return (True, data) 
        except Exception as e:
            print(e)
            return (False, None)
    else:
        return (False, None)

def is_country(input_text):
    for country in pycountry.countries:
        if input_text.lower() == getattr(country, "name").lower():
            return True
        
        if hasattr(country, "official_name") and getattr(country, "official_name").lower() == input_text.lower():
            return True
    
    return False

def is_country_code(input_text):
    if pycountry.countries.get(alpha_2 = input_text):
        return True
    
    if pycountry.countries.get(alpha_3 = input_text):
        return True

    return False


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
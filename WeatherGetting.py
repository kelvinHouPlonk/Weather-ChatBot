import requests

cities_dict = {
    "Lake District National Park":  (54.4609, 3.0886),
    "Corfe Castle":  (50.6395, 2.0566),
    "The Cotswolds":  (51.8330, 1.8433),
    "Cambridge": (52.2053, -0.1218),
    "Bristol":  (51.4545, 2.5879),
    "Oxford":  (51.7520, 1.2577),
    "Norwich": (52.6309, -1.2974),
    "Stonehenge":  (51.1789, 1.8262),
    "Watergate Bay":  (50.4429, 5.0553),
    "Birmingham":  (52.4862, 1.8904),
}

def get_weather_info(city):
    try:
        lat, lon = cities_dict[city]
        resp = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&APPID=c9408b3df80fe52ee7986cce402b4ea0")
        resp.raise_for_status()
        weather_data = resp.json()

        # Extract data for the next 20 weather updates 
        forecast = []
        for entry in weather_data['list']:
            timestamp = entry['dt']
            date = entry['dt_txt'].split()[0]
            temperature = entry['main']['temp']
            description = entry['weather'][0]['description']
            forecast.append({'timestamp': timestamp, 'date': date, 'temperature': round(temperature - 273.15, 2), 'description': description})
            
            # testing code comment out later
            """print(f"{date}: {description}, Temperature: {temperature}°C")"""

            # Break after collecting data for the next 20 weather updates
            if len(forecast) == 20:
                break

        return forecast
    except Exception as e:
        print(e)
    return None

# Example: Get weather for all cities
for city in cities_dict:
    weather_info = get_weather_info(city)
    if weather_info:
        print(f"Weather in {city}:")
        for entry in weather_info:
            print(f"{entry['date']}: {entry['description']}, Temperature: {entry['temperature']}°C")
        print("\n")
    else:
        print(f"Unable to retrieve weather information for {city}.\n")

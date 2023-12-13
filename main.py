from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

import requests

app = Flask(__name__)

# Initialize ChatterBot with specified configuration
my_bot = ChatBot(
    name="WeatherBot",
    read_only=True,
    logic_adapters=["chatterbot.logic.MathematicalEvaluation", "chatterbot.logic.BestMatch"]
)

# City lists
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

# Initialize chat history
chat_history = []

# Train the chatbot
list_trainer = ListTrainer(my_bot)

# Add small talk and weather-related conversations to the training data
small_talk = [
    "Hello",
    "Hi there!",
    "How are you?",
    "I am doing well, thank you.",
    "It’s nice to meet you!",
    "What's your name?",
    "I am a bot. You can call me WeatherBot.",
    "Goodbye",
    "Goodbye! Take care.",
    "Hi",
    "Hello there!",
    "How are you?",
    "I'm good, thanks. How about you?",
    "Nice to meet you!",
    "What's up?",
    "Hey!",
    "How's your day going?",
    "Good to see you!",
    "How's it going?",
    "Hey, how are you doing?",
    "What have you been up to?",
    "Hi, how's everything?",
    "Howdy!",
    "How's life treating you?",
    "Hello, how are things?",
    "Hi there! What's new?",
    "Hey, what's going on?",
    "What's happening?",
    "Hi, how's it going?",
    "Hey, any exciting plans?",
    "How's the weather today?",
    "Hi! What's the latest?",
    "Hello, how's your day been?",
    "Hey, anything interesting happening?",
    "Hi there! How's everything going?",
    "What's happening in your world?",
    "Hey, how's life been treating you?",
    "How's your week been so far?",
    "Hello! Anything special on your mind?",
    "Hi, any good news to share?",
    "What's new and exciting?",
    "Hey, how have you been lately?",
    "Hello! What's the gossip?",
    "Hi, what's the word?",
    "How's your week shaping up?",
    "Hey, anything fun on the horizon?",
    "Hi there! Tell me something interesting.",
    "Hello! How's your mood today?",
    "Hey, what's the vibe?",
    "How's the day treating you so far?",
    "Hi, what's the buzz?",
    "Hello! Got any cool plans?",
    "Hey, what's the talk of the town?",
    "How's everything on your end?",
]

weather_talk = [
    "What's the temperature like today?",
    "Let me check for you, what city do you want to know?",
    "Tell me about the current weather conditions.",
    "Sure let me check for you, what city would you like to know?",
    "Is it going to rain later?",
    "I will query OpenWeatherAPI for you, give me a city name",
    "What's the forecast for the week?",
    "Sure, I can help you with the weather. Could you please specify the city?",
    "How's the weather looking?",
    "Here in AI land, its always sunny, but I can also check for you your weather, just give me a city name",
    "Can you check if it will be sunny tomorrow?",
    "Where will be sunny tommorow? Give me the city name",
    "Tell me about the wind speed in Birmingham.",
    "Is it cold in Corfe Castle right now?",
    "What's the weather like in the Lake District National Park?",
    "How's the climate in Watergate Bay?",
    "What's the weather forecast for the next 7 days?",
    "Can you please tell me the city you want to know the forecast for the next 7 days for"
]

list_trainer.train(small_talk)
list_trainer.train(weather_talk)

# Function to get weather information for a specific city
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
            
            #testing code comment out later
            """print(f"{date}: {description}, Temperature: {temperature}°C")"""


            # Break after collecting data for the next 20 weather updates
            if len(forecast) == 20:
                break

        return forecast
    except Exception as e:
        print(e)
    return None

def handle_user_input(user_message):
    # Check if the user's input is small talk
    is_small_talk = any(pattern in user_message.lower() for pattern in small_talk)

    if is_small_talk:
        bot_response = my_bot.get_response(user_message)
        chat_history.append({'user': 'User', 'message': user_message, 'response': str(bot_response)})
    else:
        city_specified = False

        # Check if the user's input is a weather-related query for a specific city
        for city in cities_dict:
            if city.lower() in user_message.lower():
                weather_info = get_weather_info(city)
                if weather_info:
                    chat_history.append({'user': 'WeatherBot', 'message': f"Weather in {city}", 'response': [{'message': '', 'forecast': weather_info}]})
                    city_specified = True
                break  # Exit the loop after finding a match

        if not city_specified:
            # If the city is not specified, ask the user to specify the city
            if 'weather' in user_message.lower():
                chat_history.append({'user': 'WeatherBot', 'message': ask_for_city(), 'response': None})
            else:
                # If not a weather-related query the chatbot response without forecast
                bot_response = my_bot.get_response(user_message)
                chat_history.append({'user': 'WeatherBot', 'message': str(bot_response), 'response': None})

def ask_for_city():
    return "Sure, I can help you with the weather. Could you please specify the city?"

# Route for handling both GET and POST requests
@app.route("/", methods=['GET', 'POST'])
def weather():
    global chat_history

    if request.method == 'POST':
        user_message = request.form.get('user_message')
        handle_user_input(user_message)

    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)

from idlelib.undo import Command
from time import strftime
from API_KEY import Command_AI, News_API_KEY, Weather_API_KEY
import speech_recognition as sr
import os
import webbrowser
import datetime
import requests
import random
from google import genai


client = genai.Client(api_key=Command_AI)
chatStr = ""
def chat(query):
    global chatStr
    chatStr += f"Shubham: {query}\nLUNA: "
    try:
        # Prevent memory overflow
        if len(chatStr) > 8000:
            chatStr = chatStr[-4000:]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
You are Luna, a smart and friendly AI assistant.
Rules:
- Give only ONE final answer.
- Do NOT provide alternatives.
- Do NOT give multiple variations.
- If user asks for code, directly generate the complete code.
- Keep response clean and direct.
Conversation:
{chatStr}
"""
        )
        reply = response.text
        print(f"LUNA: {reply}")
        say(reply)
        chatStr += reply + "\n"
        return reply
    except Exception as e:
        print("Gemini Error:", e)
        return "An error occurred."

def get_weather(city):
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Weather_API_KEY}&units=metric"
        response = requests.get(weather_url, timeout=5)
        data = response.json()

        if response.status_code != 200:
            say("There is a problem with the weather API")
            return

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        air_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={Weather_API_KEY}"
        air_response = requests.get(air_url, timeout=5)
        air_data = air_response.json()

        aqi = air_data["list"][0]["main"]["aqi"]
        aqi_status = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }.get(aqi, "Unknown")

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        description = data["weather"][0]["description"]

        if temp >= 35:
            climate = "very hot climate"
        elif temp >= 25:
            climate = "warm climate"
        elif temp >= 15:
            climate = "moderate climate"
        else:
            climate = "cold climate"

        weather_report = (
            f"Weather in {city}. \n"
            f"Temperature is {temp} degree Celsius.\n "
            f"Humidity is {humidity} percent. \n"
            f"Wind speed is {wind_speed} meter per second with {description}.\n "
            f"Air Quality Index is {aqi}, which is {aqi_status}. \n"
            f"Overall it is a {climate}.\n"
        )

        print(weather_report)
        say(weather_report)

    except Exception as e:
        print("Weather Error:", e)
        say("Sorry, I could not fetch the weather and air quality.")

def get_news():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={News_API_KEY}&country=in&language=en"
        response = requests.get(url)
        data = response.json()

        if "results" not in data:
            say("There is a problem with the news API")
            return

        articles = data["results"][:5]
        for article in articles:
            title = article.get("title", "No Title")
            print(title)
            say(title)

    except Exception as e:
        print("News Error:", e)
        say("Unable to fetch news")

def write_to_file(query):
    try:
        query = query.lower()

        if "write a" in query:
            content = query.split("write a", 1)[1].strip()
        else:
            say("Please say write a")
            return

        words = content.split()
        if len(words) < 2:
            say("Please say proper sentence")
            return

        filename_part = "_".join(words[-2:])
        filename = filename_part + ".txt"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content
        )
        reply = response.text
        with open(filename, "w", encoding="utf-8") as f:
            f.write(reply)

        print(f"{filename} created successfully")
        say(f"{filename} file created successfully")

    except Exception as e:
        print("File Error:", e)
        say("Unable to create file")

def say(text):
    os.system(f"say \"{text}\"")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.....")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 1.2
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

        try:
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except:
            return ""

if __name__ == '__main__':
    print("Luna Said: Hello Shubham, how can I help you?")
    say("Hello Shubham, how can I help you?")
    while True:
        query = takeCommand()
        query.lower()

        if query == "":
            continue

        sites = [
            ["youtube", "https://www.youtube.com"],
            ["google", "https://www.google.com"],
            ["instagram", "https://www.instagram.com"],
            ["facebook", "https://www.facebook.com"],
            ["twitter", "https://www.twitter.com"],
            ["linkedin", "https://www.linkedin.com"],
            ["github", "https://www.github.com"],
            ["chatgpt", "https://chat.openai.com"],
            ["gmail", "https://mail.google.com"],
            ["stackoverflow", "https://stackoverflow.com"],
            ["wikipedia", "https://www.wikipedia.org"],
            ["amazon", "https://www.amazon.in"],
            ["flipkart", "https://www.flipkart.com"],
            ["netflix", "https://www.netflix.com"],
            ["hotstar", "https://www.hotstar.com"],
        ]

        handled = False

        for site in sites:
            if f"open {site[0]}" in query.lower():
                webbrowser.open_new_tab(site[1])
                print(f"Luna Said: OK Buddy ,Opening {site[0]}")
                say(f"O.k Buddy, Opening {site[0]}")
                handled = True
                break

        if handled:
            continue

        apps = ["Blip", "Numbers","Facetime", "Safari", "ChatGPT", "Pages", "PyCharm", "Keynote", "WhatsApp"]
        for app in apps:
            if f"open {app}".lower() in query:
                os.system(f"open -a \"{app}\"")
                print(f"Luna Said: Opening {app}")
                say(f"Opening {app}")
                handled = True
                break

        if handled:
            continue

        if "news" in query.lower() or "headline" in query.lower():
            print("Luna Said: Here are today's headlines")
            say("Here are today's headlines")
            get_news()
            continue

        if "write a" in query or "create" in query:
            print("Luna Said: Creating your text file")
            say("Creating your text file")
            write_to_file(query)
            continue

        if "play music" in query:
            music_path = "/Users/shubham_jadhav/Downloads/song1.mp3"
            os.system(f"open \"{music_path}\"")
            print("Luna Said: Playing music")
            say("Playing music")
            continue

        if " the time" in query:
            now = datetime.datetime.now()
            print(f"Luna Said:{now.strftime("%H:%M:%S")}")
            say(f"The time is {now.strftime('%H')} hours {now.strftime('%M')} minutes")
            continue

        if "the date" in query :
            today = datetime.date.today()
            print(f"Luna Said: Today's date is {today.strftime('%d-%m-%y')}")
            say(f"Today's date is {today.strftime('%d-%m-%y')}")
            continue

        if "reset chat" in query:
            chatStr = ""
            say("Chat history cleared")
            continue

        if "weather" in query:
            if "in" in query:
                city = query.split("in")[-1].strip()
                get_weather(city)
            else:
                print("Tell me the city name")
                say("Tell me the city name")
            continue

        if query.startswith("stop") or query.startswith("exit"):
            print("Luna Said: Take care Buddy, don’t forget to smile 😊")
            say("Take care Buddy, don’t forget to smile.")
            break

        if "your name" in query:
            print("Luna Said: My name is Luna 💕 ,Your personal AI Assistant")
            say("My name is Luna, Your personal A.I Assistant")
            continue

        if "hello" in query or "hi" in query:
             print("Luna Said: Hello! How can I help you today?")
             say("Hello! How can I help you today?")
             continue

        if "how are you" in query or "how r u" in query:
            print("Luna Said: I'm Luna💕, so I don't have feelings, but I'm ready to assist you!")
            say("I'm Luna, so I don't have feelings, but I'm ready to assist you!")
            continue



        chat(query)

import speech_recognition as sr
import pyttsx3
import os
import datetime
import webbrowser
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Groq setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found in .env")
    exit(1)

client = Groq(api_key=GROQ_API_KEY)

# Text-to-speech
engine = pyttsx3.init()
engine.setProperty("rate", 160)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            print("📝 Recognizing...")
            query = recognizer.recognize_google(audio, language="en-in")
            print(f"👤 You said: {query}")
            return query.lower()
        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Could not understand.")
            return None
        except sr.RequestError:
            print("Speech recognition service error.")
            return None

def chat_with_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",   # Fast and free on Groq
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

def execute_command(query):
    if not query:
        return

    # Open websites
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "wikipedia": "https://wikipedia.org"
    }
    for name, url in sites.items():
        if f"open {name}" in query:
            speak(f"Opening {name}")
            webbrowser.open(url)
            return

    # Play music
    if "play music" in query:
        music_path = os.getenv("MUSIC_PATH")
        if music_path and os.path.exists(music_path):
            os.system(f"start {music_path}")
        else:
            speak("Music file not found.")
        return

    # Time
    if "time" in query:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
        return

    # Weather
    if "weather in" in query:
        city = query.split("weather in")[-1].strip()
        api_key = os.getenv("WEATHER_API_KEY")
        if not api_key or api_key == "your_openweather_api_key_here":
            speak("Weather API key not configured.")
            return
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            data = requests.get(url).json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"In {city}, it's {temp}°C with {desc}.")
        except:
            speak("Could not fetch weather.")
        return

    # AI response
    reply = chat_with_groq(query)
    speak(reply)

if __name__ == "__main__":
    speak("Hello, I am your voice assistant powered by Groq. How can I help?")
    while True:
        cmd = listen()
        if cmd:
            if any(word in cmd for word in ["exit", "quit", "goodbye"]):
                speak("Goodbye!")
                break
            execute_command(cmd)

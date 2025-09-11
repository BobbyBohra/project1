import speech_recognition as sr
import pyttsx3
import openai
import os
import datetime
import webbrowser
import time
import requests
from dotenv import load_dotenv

# Load API Keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize TTS Engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)

# Function to make the assistant speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to user commands
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
            print("❌ No speech detected.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand.")
            return None
        except sr.RequestError:
            print("❌ Speech recognition service error.")
            return None

# Function to generate AI-based responses
def chat_with_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who provides unbiased and factual answers on all topics, including politics, science, and history."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.RateLimitError:
        time.sleep(5)
        return "Rate limit reached. Please wait and try again."
    except openai.error.OpenAIError as e:
        return f"OpenAI API error: {e}"

# Function to search Google if OpenAI fails
def search_google(query):
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"I couldn't find an answer, but I opened Google search for '{query}'."
    except Exception as e:
        return f"Google search failed: {e}"

# Function to execute user commands
def execute_command(query):
    if not query:
        return

    # Open websites
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "wikipedia": "https://www.wikipedia.com",
        "github": "https://github.com"
    }
    for site in sites:
        if f"open {site}" in query:
            speak(f"Opening {site}...")
            webbrowser.open(sites[site])
            return

    # Play music (Set your own music file path)
    if "play music" in query:
        music_path = os.getenv("MUSIC_PATH", "C:/path/to/music.mp3")
        if os.path.exists(music_path):
            os.system(f"start {music_path}")
        else:
            speak("Music file not found.")
        return

    # Tell the time
    if "time" in query:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return

    # Get weather info (Change `your_api_key` to a valid API key)
    if "weather in" in query:
        city = query.split("weather in")[-1].strip()
        api_key = os.getenv("WEATHER_API_KEY", "your_api_key")
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(weather_url).json()
        if response["cod"] == 200:
            temp = response["main"]["temp"]
            description = response["weather"][0]["description"]
            speak(f"The current temperature in {city} is {temp} degrees with {description}.")
        else:
            speak("Sorry, I couldn't fetch the weather information.")
        return

    # AI Chat Response (or Google Search if AI fails)
    response = chat_with_ai(query)
    if "OpenAI API error" in response:
        response = search_google(query)
    
    speak(response)

# Main loop
if __name__ == "__main__":
    speak("Hello! I am your voice assistant. How can I help you today?")
    while True:
        command = listen()
        if command:
            if any(word in command for word in ["exit", "quit", "goodbye", "bye"]):
                speak("Goodbye! Have a great day.")
                break
            execute_command(command)

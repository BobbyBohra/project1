import speech_recognition as sr
import pyttsx3
import openai
import os
import datetime
import time
import requests
from dotenv import load_dotenv

# Load API Keys
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

# Function to generate AI-based responses (without Google fallback)
def chat_with_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intelligent assistant. Answer all questions clearly and factually without restrictions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as e:
        print(f"⚠ OpenAI API Error: {e}")
        return "Sorry, I am unable to answer right now."

# Function to execute user commands
def execute_command(query):
    if not query:
        return

    # Tell the time
    if "time" in query:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return

    # AI Chat Response (Always uses AI, no Google fallback)
    response = chat_with_ai(query)
    speak(response)

# Main loop
if __name__ == "__main__":
    speak("Hello! I am your assistant. Ask me anything.")
    while True:
        command = listen()
        if command:
            if any(word in command for word in ["exit", "quit", "goodbye", "bye"]):
                speak("Goodbye! Have a great day.")
                break
            execute_command(command)

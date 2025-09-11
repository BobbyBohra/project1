import speech_recognition as sr
import os
import webbrowser
import openai
import pyttsx3
import datetime
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file
load_dotenv()
openai.api_key = "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"

  # Secure API key handling

# Check if API key is valid
if not openai.api_key:
    print("❌ OpenAI API key is missing! Check your .env file.")
    exit()

try:
    openai.Engine.list()
    print("✅ API key is working!")
except openai.error.AuthenticationError:
    print("❌ Invalid API key! Check your OpenAI account.")
    exit()

chatStr = "hello jarvis"

# Text-to-Speech function
def say(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()

# ChatGPT-based response function
def chat(query):
    global chatStr
    chatStr += f"Me: {query}\nJarvis: "

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jarvis, an AI assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=100
        )

        reply = response["choices"][0]["message"]["content"]
        say(reply)
        chatStr += f"{reply}\n"
    
    except openai.error.AuthenticationError:
        print("❌ Authentication error: Invalid API key.")
        say("There was an error with the API key.")
    except openai.error.RateLimitError:
        print("⏳ Rate limit exceeded. Try again later.")
        say("Rate limit exceeded. Please try again later.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        say("An unexpected error occurred.")

# Speech Recognition function
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = r.listen(source, timeout=5)  # Prevent infinite listening
            print("📝 Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"👤 User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("🤔 Sorry, I didn't catch that.")
            say("I didn't catch that. Could you repeat?")
        except sr.RequestError:
            print("⚠️ Speech Recognition API unavailable.")
            say("Speech recognition is not working.")
        except Exception as e:
            print(f"❌ Error: {e}")
            say("An error occurred.")
        return ""

# Main function
if __name__ == '__main__':
    print('🤖 Welcome to Jarvis')
    say("Welcome, Sir.")
    
    while True:
        query = takeCommand().strip()

        # Open popular websites
        sites = {
            "youtube": "https://www.youtube.com",
            "wikipedia": "https://www.wikipedia.com",
            "google": "https://www.google.com"
        }
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]} sir...")
                webbrowser.open(site[1])

        # Play music
        if "open music" in query:
            musicPath = pathlib.Path("C:/path/to/your/music/file.mp3")
            if musicPath.exists():
                os.system(f"start {musicPath}")
            else:
                say("Music file not found.")

        # Tell the time
        elif "the time" in query:
            now = datetime.datetime.now()
            say(f"Sir, the time is {now.strftime('%H')} hours and {now.strftime('%M')} minutes.")

        # Exit or reset chat
        elif "jarvis quit" in query:
            say("Goodbye, Sir.")
            break
        elif "reset chat" in query:
            chatStr = "hello jarvis"
            say("Chat history has been reset.")

        # Handle general queries
        else:
            chat(query)

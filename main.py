import speech_recognition as sr
import os
import webbrowser
import openai
import pyttsx3
import datetime
from dotenv import load_dotenv
import pathlib

# Load environment variables
load_dotenv()
openai.api_key = "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"

try:
    response = openai.Engine.list()  # Test request
    print("API key is working!")
except openai.error.AuthenticationError:
    print("Invalid API key!")

chatStr = "hello jarvis"

def say(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.say(text)
    engine.runAndWait()

def chat(query):
    global chatStr
    chatStr += f"me: {query}\n Jarvis: "
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          prompt="Your prompt here",
          max_tokens=100  # Reduce this value
   
        )
        reply = response["choices"][0]["message"]["content"]
        say(reply)
        chatStr += f"{reply}\n"
    except openai.error.AuthenticationError as e:
        print(f"Authentication error: {e}")
        say("There was an error with the API key.")
    except Exception as e:
        print(f"An error occurred: {e}")
        say("An unexpected error occurred.")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio = r.listen(source)
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query
        except Exception as e:
            print("Error:", e)
            say("I couldn't understand. Could you repeat that, please?")
            return ""

if __name__ == '__main__':
    print('Welcome to Jarvis')
    say("Welcome, Sir.")
    while True:
        query = takeCommand().strip().lower()

        # Open popular sites
        sites = [
            ["youtube", "https://www.youtube.com"],
            ["wikipedia", "https://www.wikipedia.com"],
            ["google", "https://www.google.com"]
        ]
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

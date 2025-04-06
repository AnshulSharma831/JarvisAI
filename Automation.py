from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Define constants
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Define system messages
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}. You're a content writer. Write content professionally."}]
messages = []

# Google Search
def GoogleSearch(Topic):
    search(Topic)
    return True


# Content Writing
def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)

    # Ensure the Data directory exists
    os.makedirs("Data", exist_ok=True)

    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
    return True

# YouTube Search
def YoutubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

# Play YouTube Video
def PlayYoutube(query):
    playonyt(query)
    return True

# Open Application
def OpenApp(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
    except:
        print(f"Failed to open {app}. Searching online...")
        query = f"{app} download"
        search(query)
    return True

# Close Application
def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"Failed to close {app}.")
        return False

# System Commands
def System(command):
    if command == "mute":
        keyboard.press_and_release("volume mute")
    elif command == "unmute":
        keyboard.press_and_release("volume mute")
    elif command == "volume up":
        keyboard.press_and_release("volume up")
    elif command == "volume down":
        keyboard.press_and_release("volume down")
    return True

# Translate and Execute Commands
async def TranslateAndExecute(commands):
    funcs = []
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YoutubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

# Automation
async def Automation(commands):
    async for result in TranslateAndExecute(commands):
        print(result)
    return True

# Example Usage
if __name__ == "__main__":
    commands = [
        "open chrome",
        "google search Python programming",
        "content How to write a professional email",
        "play Never Gonna Give You Up",
        "system mute"
    ]
    asyncio.run(Automation(commands))
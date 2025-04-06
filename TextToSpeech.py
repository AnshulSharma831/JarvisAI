import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Ensure the Data directory exists
if not os.path.exists("Data"):
    os.makedirs("Data")

async def TextToAudioFile(text) -> None:
    """Convert text to speech and save it as an MP3 file."""
    file_path = r"Data\speech.mp3"

    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate speech using Edge TTS
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

def TTS(Text, stop_callback=lambda: True):
    """Play text-to-speech audio using Pygame with a stop callback."""
    try:
        # Convert text to speech and save as MP3
        asyncio.run(TextToAudioFile(Text))

        # Initialize Pygame mixer
        pygame.mixer.init()

        # Load and play the MP3 file
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing or until stopped
        while pygame.mixer.music.get_busy():
            if not stop_callback():  # Check if the GUI signals to stop
                pygame.mixer.music.stop()
                return False
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        # Clean up Pygame mixer
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

def TextToSpeech(Text, stop_callback=lambda: True):
    """Handle text-to-speech for long or short text with a stop callback."""
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # Handle long text by splitting it into smaller parts
    if len(Data) > 4 and len(Text) >= 250:
        short_text = " ".join(Text.split(".")[0:2]) + ". " + random.choice(responses)
        return TTS(short_text, stop_callback)
    else:
        return TTS(Text, stop_callback)

if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
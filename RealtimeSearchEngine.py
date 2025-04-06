from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Load chat history
messages = []
if not os.path.exists("Data"):
    os.makedirs("Data")

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

def GoogleSearch(query):
    """Perform a Google search and return formatted results."""
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"

        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        print(f"Error during Google search: {e}")
        return f"Error: Unable to perform a Google search for '{query}'."

def AnswerModifier(Answer):
    """Remove empty lines from the answer."""
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    """Return real-time information as a string."""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

def RealtimeSearchEngine(prompt):
    """Handle user queries using real-time search and Groq API."""
    try:
        # Load chat history
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        # Append user query to messages
        messages.append({"role": "user", "content": prompt})

        # Perform Google search and append results to SystemChatBot
        SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

        # Get chatbot response
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        # Clean up the answer
        Answer = Answer.strip().replace("</s>", "")

        # Append assistant's response to messages
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat history
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        # Remove Google search results from SystemChatBot
        SystemChatBot.pop()

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, an error occurred. Please try again."

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        if prompt.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(RealtimeSearchEngine(prompt))
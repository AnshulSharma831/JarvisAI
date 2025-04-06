import cohere
from rich import print
from dotenv import dotenv_values


env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")


if not CohereAPIKey:
    raise ValueError("CohereAPIKey is missing from .env file!")


co = cohere.Client(api_key=CohereAPIKey)


funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search", "youtube search",
    "reminder"
]


preamble = """ 
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
*** Do not answer any query, just decide what kind of query it is. ***

-> Respond with 'general ( query )' if a query can be answered by an LLM (AI chatbot).
-> Respond with 'realtime ( query )' if a query requires up-to-date information.
-> Respond with 'open (application name)' if a query asks to open an app.
-> Respond with 'close (application name)' if a query asks to close an app.
-> Respond with 'play (song name)' if a query asks to play a song.
-> Respond with 'generate image (image prompt)' if a query asks to generate an image.
-> Respond with 'reminder (datetime with message)' if a query asks to set a reminder.
-> Respond with 'system (task name)' if a query asks to control system settings.
-> Respond with 'content (topic)' if a query asks for generated content.
-> Respond with 'google search (topic)' if a query asks to search on Google.
-> Respond with 'youtube search (topic)' if a query asks to search on YouTube.
-> Respond with 'exit' if the user says goodbye.

*** If the query doesn't match any rule, respond with 'general (query)' ***
"""


ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "what is today's date and remind me about my performance on 5th Aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th Aug dancing performance"},
]

def FirstLayerDMM(prompt: str = "test"):
    """Processes the user query and classifies it into predefined categories."""
    
    try:
        
        response = co.chat(
            model='command-r-plus',
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble
        )
        
       
        response_text = response.text
        
    except Exception as e:
        print(f"[red]Error communicating with Cohere API: {e}[/red]")
        return ["error"]

    print("[green]Raw response from Cohere:[/green]", response_text)


    if not response_text.strip():
        print("[yellow]Warning: Empty response from Cohere![/yellow]")
        return ["error"]


    response_text = response_text.replace("\n", "").split(",")
    response_text = [i.strip() for i in response_text]

 
    temp = []
    for task in response_text:
        if any(task.startswith(func) for func in funcs):
            temp.append(task)

   
    if not temp:
        print("[yellow]Warning: No matching response found, defaulting to 'general'.[/yellow]")
        return [f"general {prompt}"]

 
    if any("(query)" in res for res in temp):
        print("[yellow]Warning: Response contains '(query)', returning 'general' as fallback.[/yellow]")
        return [f"general {prompt}"]

    return temp

if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(FirstLayerDMM(user_input))
import os
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from groq import Groq

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL")

client = Groq(
    api_key=GROQ_API_KEY 
)


def get_groq_response(prompt):
    try:
        response = groq_llm_api_call(prompt)
        return response.strip()
    except Exception as e:
        return f"Error: {e}"

def groq_llm_api_call(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You reply in 50 words or less in the language the user sends you."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=MODEL,
    )
    return chat_completion.choices[0].message.content

def chat_with_groq_llm():
    session = PromptSession(history=InMemoryHistory())
    style = Style.from_dict({
        'prompt': 'ansicyan bold',  # Prompt color/style
        'response': 'ansigreen',    # Response color/style
    })
    print("Welcome to Groq LLM Chat! Type 'exit' to quit.\n")
    while True:
        try:
            prompt = session.prompt('You: ')
            if prompt.lower() in ['exit', 'quit']:
                print("Exiting Groq LLM Chat. Goodbye!")
                break
            response = get_groq_response(prompt)
            print(f"\033[92mGroq LLM: {response}\033[0m\n")  # Using ANSI for colors
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Groq LLM Chat. Goodbye!")
            break

if __name__ == "__main__":
    chat_with_groq_llm()


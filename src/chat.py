import os
from datetime import datetime

from dotenv import load_dotenv  # Ensure this import is here
from groq import Groq
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

# Load environment variables from .env file
load_dotenv()

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL")

client = Groq(api_key=GROQ_API_KEY)


# Function to get response from Groq, using conversation history
def get_groq_response(conversation_history):
    try:
        response = groq_llm_api_call(conversation_history)
        return response.strip()
    except Exception as e:
        return f"Error: {e}"


# API call with conversation history
def groq_llm_api_call(conversation_history):
    chat_completion = client.chat.completions.create(
        messages=conversation_history,
        model=MODEL,
    )
    return chat_completion.choices[0].message.content


# Main chat function with history
def chat_with_groq_llm():
    session = PromptSession(history=InMemoryHistory())
    style = Style.from_dict(
        {
            "prompt": "ansicyan bold",  # Prompt color/style
            "response": "ansigreen",  # Response color/style
        }
    )

    # Initialize conversation history
    conversation_history = [
        {
            "role": "system",
            "content": "You reply in 50 words or less in the language the user sends you.",
        }
    ]

    # Set logging flag
    logging_enabled = False

    print(
        "Welcome to Groq LLM Chat! Type 'exit' to quit, 'start evaluation' to begin logging, or 'stop evaluation' to stop logging.\n"
    )
    while True:
        try:
            prompt = session.prompt("You: ")
            if prompt.lower() == "exit":
                print("Exiting Groq LLM Chat. Goodbye!")
                break
            elif prompt.lower() == "start evaluation":
                logging_enabled = True
                print("Evaluation logging started.")
                continue
            elif prompt.lower() == "stop evaluation":
                logging_enabled = False
                print("Evaluation logging stopped.")
                continue

            # Add user message to the conversation history
            conversation_history.append({"role": "user", "content": prompt})

            # Get response from Groq LLM
            response = get_groq_response(conversation_history)

            # Display response
            print(f"\033[92mGroq LLM: {response}\033[0m\n")  # Using ANSI for colors

            # Add response to conversation history
            conversation_history.append({"role": "assistant", "content": response})

        except (EOFError, KeyboardInterrupt):
            print("\nExiting Groq LLM Chat. Goodbye!")
            break


if __name__ == "__main__":
    chat_with_groq_llm()

import os
import argparse
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from groq import Groq
import psycopg2
from datetime import datetime

load_dotenv()

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PW = os.getenv("POSTGRES_PW")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

client = Groq(api_key=GROQ_API_KEY)

# Connect to PostgreSQL
def create_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PW,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Log conversation to PostgreSQL
def log_conversation_to_db(username, prompt, response):
    conn = create_db_connection()
    if conn is None:
        print("Could not connect to database.")
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversations (username, prompt, response, created_at) VALUES (%s, %s, %s, %s)",
                (username, prompt, response, datetime.now())
            )
            conn.commit()
    except Exception as e:
        print(f"Error logging conversation: {e}")
    finally:
        conn.close()

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
def chat_with_groq_llm(username):
    session = PromptSession(history=InMemoryHistory())
    style = Style.from_dict({
        'prompt': 'ansicyan bold',  # Prompt color/style
        'response': 'ansigreen',    # Response color/style
    })

    # Initialize conversation history
    conversation_history = [
        {
            "role": "system",
            "content": "You reply in 50 words or less in the language the user sends you."
        }
    ]

    # Set logging flag
    logging_enabled = False

    print("Welcome to Groq LLM Chat! Type 'exit' to quit, 'start evaluation' to begin logging, or 'stop evaluation' to stop logging.\n")
    while True:
        try:
            prompt = session.prompt('You: ')
            if prompt.lower() == 'exit':
                print("Exiting Groq LLM Chat. Goodbye!")
                break
            elif prompt.lower() == 'start evaluation':
                logging_enabled = True
                print("Evaluation logging started.")
                continue
            elif prompt.lower() == 'stop evaluation':
                logging_enabled = False
                print("Evaluation logging stopped.")
                continue

            # Add user message to the conversation history
            conversation_history.append({"role": "user", "content": prompt})

            # Get response from Groq LLM
            response = get_groq_response(conversation_history)

            # Display response
            print(f"\033[92mGroq LLM: {response}\033[0m\n")  # Using ANSI for colors

            # Log conversation in the database if logging is enabled
            if logging_enabled:
                log_conversation_to_db(username, prompt, response)

            # Add response to conversation history
            conversation_history.append({"role": "assistant", "content": response})

        except (EOFError, KeyboardInterrupt):
            print("\nExiting Groq LLM Chat. Goodbye!")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with Groq LLM and log conversations.")
    parser.add_argument('-u', '--user', required=True, help="Specify the username for logging")
    args = parser.parse_args()

    chat_with_groq_llm(args.user)


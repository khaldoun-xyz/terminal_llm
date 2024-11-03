# provide llm with chat history & get report on progress
import argparse
import os

import psycopg2
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PW = os.getenv("POSTGRES_PW")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Connect to PostgreSQL and retrieve conversation history
def get_conversation_history(username):
    conn = None
    conversation_history = []
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PW,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
        )
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT prompt FROM conversations WHERE username = %s", (username,)
            )
            conversation_history = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
    finally:
        if conn:
            conn.close()
    return conversation_history


# Send request to LLM for language proficiency evaluation
def evaluate_language_proficiency(conversation_history, language):
    if not conversation_history:
        return "No conversation history available for evaluation."

    # Format conversation history for prompt
    formatted_history = "\n".join(conversation_history)
    prompt = (
        f"Based on the following conversation history, rate the {language} proficiency of the user on a scale from 0 to 100 and only consider the messages in that language, "
        "mentioning their strong and weak points:\n\n"
        f"{formatted_history}\n\n"
    )

    # LLM API call
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert language evaluator."},
                {"role": "user", "content": prompt},
            ],
            model=MODEL,
        )
        response = chat_completion.choices[0].message.content
        return response.strip()
    except Exception as e:
        return f"Error during LLM evaluation: {e}"


if __name__ == "__main__":
    # Define command-line arguments
    parser = argparse.ArgumentParser(
        description="Evaluate a user's language proficiency based on conversation history."
    )
    parser.add_argument("-u", "--username", required=True, help="Username to evaluate")
    parser.add_argument(
        "-l",
        "--language",
        required=True,
        help="Language to evaluate (e.g., English, French, German)",
    )

    args = parser.parse_args()

    # Get arguments from user input
    username = args.username
    language = args.language

    # Fetch conversation history and evaluate proficiency
    history = get_conversation_history(username)
    evaluation = evaluate_language_proficiency(history, language)
    print(evaluation)

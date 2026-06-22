from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)


def get_response(history, message):
    try:
        if not message or not message.strip():
            return "Error: Empty message provided"

        conversation = "\n".join(history[-10:])

        prompt = f"""
Previous Conversation:
{conversation}

Current User Message:
{message}

Answer based on the conversation context if relevant.
"""

        response = llm.invoke(prompt)

        return response.content

    except Exception as e:
        logger.error(f"Error getting response from LLM: {str(e)}")
        return "Error: Unable to process your request. Please try again later."
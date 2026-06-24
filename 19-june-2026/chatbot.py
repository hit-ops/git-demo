from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import google_search
import logging

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

llm_with_tools = llm.bind_tools(
    [google_search]
)

tool_map = {
    "google_search": google_search
}


def extract_text(response):
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text = ""

        for item in content:
            if isinstance(item, dict):
                text += item.get("text", "")
            else:
                text += str(item)

        return text

    return str(content)


def get_response(history, message):
    try:
        if not message or not message.strip():
            return "Error: Empty message provided"

        # Use last 4 messages as context
        conversation = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in history[-4:]
        )

        prompt = f"""
You are a helpful assistant with access to external tools.

Use external tools only when the question requires
recent, live, or changing information.

Context:
{conversation}

Question:
{message}
"""

        response = llm_with_tools.invoke(prompt)

        logger.info(
            f"Tool calls: {response.tool_calls}"
        )

        # Tool was called
        if response.tool_calls:
            tool_call = response.tool_calls[0]

            logger.info(
                f"Tool called: {tool_call['name']}"
            )

            tool = tool_map.get(
                tool_call["name"]
            )

            if tool:
                tool_result = tool.invoke(
                    tool_call["args"]
                )

                final_prompt = f"""
Question:
{message}

Search Results:
{tool_result}

Answer the question using the search results.
"""

                final_response = llm.invoke(
                    final_prompt
                )

                return extract_text(
                    final_response
                )

        # No tool required
        result = extract_text(response)

        return (
            result
            or "No response generated."
        )

    except Exception as e:
        logger.exception(
            "Error getting response"
        )

        return (
            "Error: Unable to process your request."
        )
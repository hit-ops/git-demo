from langchain.tools import tool
from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()


@tool
def google_search(query: str):
    """
    Search Google for recent or real-time information such as
    news, weather, stock prices, current events, and live data.
    """

    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" not in results:
        return "No results found."

    output = []

    for item in results["organic_results"][:3]:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")

        output.append(
            f"Title: {title}\n"
            f"Link: {link}\n"
            f"Snippet: {snippet}"
        )

    return "\n\n".join(output)
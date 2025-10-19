
# import os
# import httpx
# import logging
# from dotenv import load_dotenv
# from livekit.agents import function_tool
# from datetime import datetime

# # 🔹 Load environment variables from .env
# load_dotenv()

# # 🔹 Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # 🔹 Auto-fill env variables (अगर missing हैं तो fallback भी लगा दिया है)
# GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "AIzaSyBmkNcI9ev65Mt-OEKsfxhwEjXK8zydJ_4")
# SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID", "25b9df1322ca54a5c")

# @function_tool
# async def google_search(query: str) -> str:
#     """
#     Google Custom Search API के द्वारा results लाने का function।
#     """

#     if not GOOGLE_SEARCH_API_KEY or not SEARCH_ENGINE_ID:
#         return "❌ Google Search API key या Search Engine ID missing है।"

#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "key": GOOGLE_SEARCH_API_KEY,
#         "cx": SEARCH_ENGINE_ID,
#         "q": query,
#         "num": 10  # ज़्यादा results चाहिए तो बदल सकते हो (max 10)
#     }

#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.get(url, params=params)
#             response.raise_for_status()
#     except httpx.RequestError as e:
#         logger.error(f"Network error: {e}")
#         return f"❌ Network error: {e}"
#     except httpx.HTTPStatusError as e:
#         logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
#         return f"❌ Google API error: {e.response.status_code} - {e.response.text}"

#     data = response.json()
#     results = data.get("items", [])

#     if not results:
#         logger.info("No results found.")
#         return "ℹ️ कोई results नहीं मिले।"

#     # 🔹 Markdown style formatting
#     formatted = "\n".join(
#         [f"**{i+1}. {item.get('title','No title')}**\n🔗 {item.get('link','No link')}\n📌 {item.get('snippet','')}\n"
#          for i, item in enumerate(results)]
#     )

#     return formatted.strip()


# @function_tool
# async def get_current_datetime() -> str:
#     """Current datetime ISO format में return करेगा"""
#     return datetime.now().isoformat()


import os
import requests
import logging
from dotenv import load_dotenv
from livekit.agents import function_tool  # ✅ Correct decorator
from datetime import datetime
from livekit import agents

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import requests
import logging
from livekit.agents import function_tool
from langchain.tools import tool

logger = logging.getLogger(__name__)

@tool
async def google_search(query: str) -> str:
    """
    Searches Google and returns the top 3 results with heading and summary only.
    No raw links are included to make speech output sound natural.
    """

    logger.info(f"Query प्राप्त हुई: {query}")

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        missing = []
        if not api_key:
            missing.append("GOOGLE_SEARCH_API_KEY")
        if not search_engine_id:
            missing.append("SEARCH_ENGINE_ID")
        return f"Missing environment variables: {', '.join(missing)}"

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "num": 3
    }

    try:
        logger.info("Google Custom Search API को request भेजी जा रही है...")
        response = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return f"Google Search API request failed: {e}"

    if response.status_code != 200:
        logger.error(f"Google API error: {response.status_code} - {response.text}")
        return f"Google Search API में error आया: {response.status_code} - {response.text}"

    data = response.json()
    results = data.get("items", [])

    if not results:
        logger.info("कोई results नहीं मिले।")
        return "कोई results नहीं मिले।"

    # Create a natural, speech-friendly summary
    formatted = "Here are the top results:\n"
    for i, item in enumerate(results, start=1):
        title = item.get("title", "No title")
        snippet = item.get("snippet", "").strip()
        formatted += f"{i}. {title}. {snippet}\n\n"

    return formatted.strip()

@tool
async def get_current_datetime() -> str:
    """
    Returns the current date and time in a human-readable format.

    Use this tool when the user asks for the current time, date, or wants to know what day it is.
    Example prompts:
    - "अब क्या time हो रहा है?"
    - "आज की तारीख क्या है?"
    - "What’s the time right now?"
    """

    now = datetime.now()
    formatted = now.strftime("%d %B %Y, %I:%M %p")  # Example: 31 July 2025, 04:22 PM
    return formatted
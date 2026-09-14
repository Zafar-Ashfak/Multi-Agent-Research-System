from langchain.tools import tool
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
import os
from rich import print

from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

# Creating tool for searching information and links
@tool
def web_search(query : str) -> str:
    """
    Search the web for recent and reliable information in a topic.
    Return Titles, URLs, and Snippets.
    """

    results = tavily.search(query, max_results=3)
    outputs = []
    br = "\n____________________________________________________________________________________________\n"
    for r in results['results']:
        outputs.append(
            f"URL: {r['url']}\n\nTitle: {r['title']}\n\nContent: {r['content'][:500]}\r"
        )

    return br.join(outputs)


print(web_search.invoke('What is NLP in AI?'))
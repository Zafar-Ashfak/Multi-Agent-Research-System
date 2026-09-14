from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from rich import print

from dotenv import load_dotenv
load_dotenv()

tavily = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

# Creating tool
@tool
def web_search(query : str) -> str:
    """
    Search the web for recent and reliable information in a topic.
    Return Titles, URLs, and Snippets.
    """

    results = tavily.search(query=query, max_results=3)
    out = []
    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\r"
        )

    return "\n------\n.".join(out)

print(web_search.invoke('What is RAG'))

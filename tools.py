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

@tool
def scrape_website(url: str) -> str:
    """
    Scrape and extract readable text content from a website URL.
    """

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove elements that don't contain useful page text
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        return text[:5000]

    except requests.RequestException as e:
        return f"Error scraping website: {e}"

print(
    scrape_website.invoke("https://www.coursera.org/articles/what-is-hugging-face")
)


# print(web_search.invoke('What is NLP in AI?'))
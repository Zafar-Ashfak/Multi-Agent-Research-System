from langchain.tools import tool
from tavily import TavilyClient
import requests
from bs4 import BeautifulSoup
import os

from dotenv import load_dotenv

load_dotenv()


tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


# Creating tool for searching information and links
@tool
def web_search(query: str) -> str:
    """
    Search the web for reliable and detailed information.
    """

    search_query = (
        f"{query}. "
        f"Find sources that directly explain and define the topic. "
        f"Prefer authoritative technical documentation, university "
        f"courses, academic research papers, and major technology "
        f"research organizations. "
        f"Do not return pages about how to find research papers, "
        f"research paper lists, discussion forums, Reddit, Quora, "
        f"or generic research guides."
    )

    results = tavily.search(
        search_query,
        max_results=10,
        search_depth="advanced"
    )

    outputs = []
    seen_urls = set()

    separator = "\n" + "_" * 100 + "\n"

    for result in results["results"]:

        url = result.get("url", "").strip()

        if not url:
            continue

        # Remove duplicate URLs
        if url in seen_urls:
            continue

        seen_urls.add(url)

        title = result.get("title", "").strip()
        content = result.get("content", "") or ""
        raw_content = result.get("raw_content") or ""

        outputs.append(
            f"URL: {url}\n\n"
            f"Title: {title}\n\n"
            f"Content: {content[:1000]}\n\n"
            f"RAW_CONTENT: {raw_content[:5000]}"
        )

    return separator.join(outputs)


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

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove elements that don't contain useful page text
        for element in soup(
            ["script", "style", "nav", "footer", "header"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:5000]

    except requests.RequestException as e:
        return f"Error scraping website: {e}"
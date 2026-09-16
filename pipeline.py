import re

from agents import writer_chain, critic_chain
from tools import web_search, scrape_url


def extract_urls(search_results: str) -> list[str]:
    """
    Extract URLs from Tavily search results.
    """
    urls = re.findall(r"URL:\s*(https?://\S+)", search_results)

    # Remove duplicates while preserving order
    unique_urls = []

    for url in urls:
        url = url.rstrip(".,);]")

        if url not in unique_urls:
            unique_urls.append(url)

    return unique_urls


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ==================================================
    # STEP 1 - WEB SEARCH
    # ==================================================

    print("\n" + "=" * 60)
    print("STEP 1 - SEARCHING THE WEB")
    print("=" * 60)

    state["search_results"] = web_search.invoke({
        "query": topic
    })

    print("\nSearch Results:\n")
    print(state["search_results"])


    # ==================================================
    # STEP 2 - SELECT + SCRAPE SOURCES
    # ==================================================

    print("\n" + "=" * 60)
    print("STEP 2 - READING TOP SOURCES")
    print("=" * 60)

    urls = extract_urls(state["search_results"])

    if not urls:
        raise ValueError("No URLs were found in the search results.")

    # Keep the research reasonably fast.
    # We scrape the top 3 sources returned by Tavily.
    selected_urls = urls[:3]

    scraped_sources = []

    for index, url in enumerate(selected_urls, start=1):

        print(f"\nReading source {index}/{len(selected_urls)}:")
        print(url)

        content = scrape_url.invoke({
            "url": url
        })

        scraped_sources.append(
            f"""
SOURCE {index}
URL: {url}

CONTENT:
{content}
"""
        )

    state["scraped_content"] = "\n\n" + "\n\n".join(scraped_sources)

    print("\nScraped Research:\n")
    print(state["scraped_content"])


    # ==================================================
    # STEP 3 - WRITER
    # ==================================================

    print("\n" + "=" * 60)
    print("STEP 3 - WRITER IS DRAFTING THE REPORT")
    print("=" * 60)

    research_combined = (
        f"""
SEARCH RESULTS:
{state["search_results"]}

DETAILED SCRAPED CONTENT:
{state["scraped_content"]}
"""
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n")
    print(state["report"])


    # ==================================================
    # STEP 4 - CRITIC
    # ==================================================

    print("\n" + "=" * 60)
    print("STEP 4 - CRITIC IS REVIEWING THE REPORT")
    print("=" * 60)

    state["feedback"] = critic_chain.invoke({
        "topic": topic,
        "research": research_combined,
        "report": state["report"]
    })

    print("\nCritic Report:\n")
    print(state["feedback"])


    return state


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    topic = input("\nEnter a research topic: ").strip()

    if not topic:
        print("Please enter a research topic.")
    else:
        run_research_pipeline(topic)
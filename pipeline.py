from agents import reader_chain, writer_chain, critic_chain
from tools import web_search, scrape_website

import re


def extract_sources(search_results: str) -> list:
    """
    Extract URLs and titles from Tavily search output.
    """

    sources = []

    blocks = search_results.split("\n" + "_" * 100 + "\n")

    for block in blocks:

        url_match = re.search(
            r"URL:\s*(https?://\S+)",
            block
        )

        title_match = re.search(
            r"Title:\s*(.+)",
            block
        )

        if url_match:
            url = url_match.group(1).strip()

            title = (
                title_match.group(1).strip()
                if title_match
                else "Unknown"
            )

            sources.append({
                "title": title,
                "url": url
            })

    return sources


def score_source(source: dict) -> int:
    """
    Score a source based on authority and relevance.
    """

    url = source["url"].lower()
    title = source["title"].lower()

    score = 0

    # -------------------------
    # AUTHORITY
    # -------------------------

    if ".gov" in url:
        score += 20

    if ".edu" in url:
        score += 15

    if "arxiv.org" in url:
        score += 15

    if "acm.org" in url:
        score += 15

    if "ieee.org" in url:
        score += 15

    if "developers." in url:
        score += 12

    if "docs." in url:
        score += 12

    if "aws.amazon.com" in url:
        score += 12

    if "cloud.google.com" in url:
        score += 12

    if "learn.microsoft.com" in url:
        score += 12

    if "nvidia.com" in url:
        score += 10

    if "ibm.com" in url:
        score += 10

    # -------------------------
    # TECHNICAL SOURCES
    # -------------------------

    if "research" in url:
        score += 8

    if "documentation" in url:
        score += 8

    if "/blog/" in url:
        score += 3

    # -------------------------
    # TOPIC RELEVANCE
    # -------------------------

    relevant_keywords = [
        "deep learning",
        "deep-learning",
        "neural network",
        "machine learning"
    ]

    for keyword in relevant_keywords:

        if keyword in title:
            score += 5

        if keyword in url:
            score += 3

    # -------------------------
    # BAD SOURCES
    # -------------------------

    bad_domains = [
        "quora.com",
        "reddit.com",
        "medium.com",
        "papersowl.com",
        "kdnuggets.com",
        "github.com"
    ]

    for domain in bad_domains:

        if domain in url:
            score -= 30

    # -------------------------
    # IRRELEVANT CONTENT
    # -------------------------

    bad_keywords = [
        "how to find",
        "where can i find",
        "find sources",
        "research paper guide",
        "rate my professor",
        "product"
    ]

    for keyword in bad_keywords:

        if keyword in title:
            score -= 25

    return score

def select_sources(sources: list, limit: int = 3) -> list:

    ranked = sorted(
        sources,
        key=score_source,
        reverse=True
    )

    selected = []
    seen_domains = set()

    for source in ranked:

        match = re.search(
            r"https?://(?:www\.)?([^/]+)",
            source["url"]
        )

        domain = match.group(1) if match else source["url"]

        if domain in seen_domains:
            continue

        seen_domains.add(domain)
        selected.append(source)

        if len(selected) >= limit:
            break

    return selected

def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ==========================================
    # SEARCH
    # ==========================================

    print("\n" + "=" * 60)
    print("SEARCH AGENT")
    print("=" * 60)

    state["search_results"] = web_search.invoke(
        f"""
    Research the topic: {topic}

    Find sources that directly explain:
    - What the topic is
    - How it works
    - Key components
    - Practical applications
    - Benefits
    - Limitations

    Prefer:
    - Official documentation
    - Academic or research papers
    - Government sources
    - Educational sources
    - Reputable technical organizations

    Avoid:
    - Marketing pages
    - Product pages
    - Irrelevant GitHub projects
    - Promotional articles
    - Duplicate sources
    """
    )

    print("\nSearch completed.")

    # ==========================================
    # EXTRACT SOURCES
    # ==========================================

    all_sources = extract_sources(
        state["search_results"]
    )

    print("\nFound sources:")

    for source in all_sources:
        print(
            f"- {source['title']}\n"
            f"  {source['url']}"
        )

    # ==========================================
    # SELECT BEST SOURCES
    # ==========================================

    state["selected_sources"] = select_sources(
        all_sources,
        limit=3
    )

    print("\n" + "=" * 60)
    print("SELECTED SOURCES")
    print("=" * 60)

    for source in state["selected_sources"]:
        print(
            f"\n{source['title']}\n"
            f"{source['url']}"
        )

    # ==========================================
    # SCRAPE SOURCES
    # ==========================================

    print("\n" + "=" * 60)
    print("READER - SCRAPING SOURCES")
    print("=" * 60)

    scraped_sources = []

    for source in state["selected_sources"]:

        print(f"\nScraping: {source['url']}")

        content = scrape_website.invoke(
            source["url"]
        )

        scraped_sources.append({
            "title": source["title"],
            "url": source["url"],
            "content": content
        })

    state["scraped_sources"] = scraped_sources

    # ==========================================
    # READER
    # ==========================================

    print("\n" + "=" * 60)
    print("READER - ANALYZING SOURCES")
    print("=" * 60)

    research_text = ""

    for i, source in enumerate(
        state["scraped_sources"],
        start=1
    ):

        research_text += f"""

================ SOURCE {i} ================

Title:
{source['title']}

URL:
{source['url']}

Content:
{source['content']}

================================================
"""

    state["research"] = reader_chain.invoke({
        "topic": topic,
        "research": research_text
    })

    print("\nResearch analysis completed.")

    # ==========================================
    # WRITER
    # ==========================================

    print("\n" + "=" * 60)
    print("WRITER")
    print("=" * 60)

    verified_urls = "\n".join(
        source["url"]
        for source in state["selected_sources"]
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": state["research"],
        "sources": verified_urls
    })

    print("\nFinal Report:\n")
    print(state["report"])

    # ==========================================
    # CRITIC
    # ==========================================

    print("\n" + "=" * 60)
    print("CRITIC")
    print("=" * 60)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCritic Report:\n")
    print(state["feedback"])

    return state


if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    run_research_pipeline(topic)
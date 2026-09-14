from agents import build_reader_agent, build_search_agent
from agents import writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    # search agent working
    print("\n" + "=" * 50)
    print("Search agent is working...")
    print("\n" + "=" * 50)

    search_agent = build_search_agent()
    search_result =  search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })


    state['search_results'] = search_result['messages'][-1].content
    print("\nSearch result", state['search_results'])

    # reader agent
    print("\n" + "=" * 50)
    print("Reader agent is scrapping top resources...")
    print("=" * 50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
                      f"Based on the following search results about '{topic}',"
                      f"Pick the most relevant URL and scrape it for deeper content.\n\n"
                      f"Search Results:\n{state['search_results'][:800]}"
                    )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nScraped Content: \n", state['scraped_content'])
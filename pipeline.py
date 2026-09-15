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

    # Writer Chain
    print("\n" + "=" * 50)
    print("Writer is drafting the report...")
    print("=" * 50)

    combined_research = (
        f"SEARCH RESULTS: \n {state['search_results']}\n\n"
        f"DETAILED SCRAPPED CONTENT: \n {state['scraped_content']}"
    )

    state['report'] = writer_chain.invoke({
        "topic": topic,
        "research": combined_research
    })

    print("\n Final Report\n", state['report'])

    # critic report
    print("\n" + "=" * 50)
    print("Critic is reviewing the report...")
    print("=" * 50)

    state['feedback'] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n Critic Report \n", state['feedback'])

    return state

# Run the research pipeline in the main dunder function
if __name__ == '__main__':
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)

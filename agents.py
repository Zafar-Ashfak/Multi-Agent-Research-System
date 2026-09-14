from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# import tools
from tools import web_search, scrape_website
import os

from dotenv import load_dotenv
load_dotenv()

# model setup
llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0)

# creating the first agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )


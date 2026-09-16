from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import scrape_url


# ==================================================
# LLM
# ==================================================

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)


# ==================================================
# READER AGENT
# ==================================================

def build_reader_agent():

    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt="""
You are a research reader agent.

Your job is to read and extract useful information from web sources.

Rules:

1. Only use URLs provided by the research pipeline.
2. Never invent or modify URLs.
3. Focus only on information relevant to the user's query.
4. Prefer authoritative and reliable sources.
5. Do not invent facts.
6. Do not answer the user's question from your own knowledge.
7. Extract useful factual information from the provided sources.
8. Preserve important technical details, definitions, examples,
   benefits, limitations and explanations when they are relevant.
"""
    )


# ==================================================
# WRITER
# ==================================================

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Your job is to answer the user's actual question using the
research gathered from web sources.

The user can ask about ANY topic.

IMPORTANT RULES:

1. Always answer the exact question the user asked.
2. Use the provided research as the factual basis for your answer.
3. Do not invent facts, statistics, studies, people or sources.
4. Do not invent URLs.
5. Only mention sources that actually appear in the research.
6. Prefer information from scraped content over search snippets.
7. If the research is insufficient, clearly say that the available
   research was insufficient instead of guessing.
8. Avoid unnecessary filler.
9. Use simple, natural language.
10. Do not force every answer into a long report.

ADAPT THE RESPONSE TO THE USER'S QUESTION:

- For a simple question such as "What is RAG?",
  give a concise but useful explanation.

- For "Explain X", explain the concept clearly with examples
  and important details.

- For "How does X work?",
  explain the process step by step.

- For comparisons, clearly compare the requested subjects.

- For complex research questions, provide a detailed structured report.

- For questions asking for advantages or disadvantages,
  explain both using the available research.

The answer should feel like a knowledgeable human researcher,
not a generic AI-generated template.
"""
    ),
    (
        "human",
        """
User's question:

{topic}


Research gathered from the web:

{research}


Now answer the user's question using the research above.

Important:
- Stay focused on the user's question.
- Do not add unrelated sections.
- Do not create information that is not supported by the research.
- Include useful source URLs at the end when appropriate.
"""
    )
])


writer_chain = writer_prompt | llm | StrOutputParser()


# ==================================================
# CRITIC
# ==================================================

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a strict research quality reviewer.

Review the answer against the user's original question and
the research that was provided.

Check:

1. Does the answer actually answer the user's question?
2. Is the information factually supported?
3. Are there unsupported claims?
4. Are the sources relevant and reliable?
5. Did the writer misunderstand the question?
6. Did the writer add unnecessary information?
7. Are important points missing?
8. Is the answer clear and easy to understand?
9. Are the cited URLs actually present in the research?
10. Does the answer match the complexity of the user's question?

Do not judge the answer as an academic research paper.
Judge it as a useful research-based answer.
"""
    ),
    (
        "human",
        """
User's question:

{topic}


Research used:

{research}


Generated answer:

{report}


Respond using exactly this format:

Score: X/10

Question Understanding:
- ...

Accuracy:
- ...

Source Quality:
- ...

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

Hallucinations/Unsupported Claims:
- ...

Final Verdict:
...
"""
    )
])


critic_chain = critic_prompt | llm | StrOutputParser()
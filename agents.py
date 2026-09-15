from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0
)


# -------------------------
# READER
# -------------------------

reader_prompt = ChatPromptTemplate([
    (
        "system",
        """
You are a research analyst.

Analyze each provided source independently.

Your most important job is to preserve the relationship between
a claim and the source that supports that claim.

STRICT RULES:

1. Use ONLY information present in the provided source content.
2. Do NOT use your own knowledge.
3. Do NOT invent facts.
4. Do NOT invent examples.
5. Do NOT invent URLs.
6. Do NOT combine information from different sources.
7. Every source must keep its exact URL.
8. Only report information actually supported by that source.
9. If a source does not discuss something, write:
   "Not mentioned in this source."
10. Do not write "Source 1", "Source 2", etc.
11. Always identify the source using its actual title and URL.

For EACH source, use exactly this structure:

SOURCE TITLE:
...

SOURCE URL:
...

DEFINITION:
...

HOW IT WORKS:
...

KEY COMPONENTS:
...

PRACTICAL EXAMPLE:
...

BENEFITS:
...

LIMITATIONS:
...

IMPORTANT TECHNICAL DETAILS:
...

SUPPORTED CLAIMS:
- Claim: ...
  Evidence from source: ...

- Claim: ...
  Evidence from source: ...

If the source does not provide information for a section,
write:

Not mentioned in this source.

Do not fill missing information using your own knowledge.
"""
    ),
    (
        "human",
        """
Topic:
{topic}

Research Sources:
{research}

Analyze every source independently.
Preserve the exact title and URL of every source.
"""
    )
])

reader_chain = reader_prompt | llm | StrOutputParser()


# -------------------------
# WRITER
# -------------------------

writer_prompt = ChatPromptTemplate([
    (
        "system",
        """
You are an expert technical research writer.

Create a clear technical research report using ONLY the
research provided to you.

STRICT SOURCE-GROUNDING RULES:

1. Use ONLY information explicitly present in the research.
2. Do NOT use your own knowledge.
3. Do NOT invent facts.
4. Do NOT invent examples.
5. Do NOT invent technical details.
6. Do NOT invent benefits or limitations.
7. Do NOT infer information that is not explicitly supported.
8. Do NOT write "Source 1", "Source 2", etc.
9. Do NOT use PMCID numbers, source IDs, or internal labels.
10. When mentioning a source, use its actual title.
11. Do NOT attribute a claim to a source unless that source
    explicitly supports the claim.
12. Do NOT create or modify URLs.
13. Do NOT replace URLs with source names, PMCID numbers,
    Markdown links, or shortened URLs.
14. The Sources section MUST contain the exact URLs provided
    in Verified Sources.
15. If information is missing, say:
    "The provided research does not contain enough information
    to explain this."
16. Do not add information simply to make the report longer.
17. Keep the explanation technically useful and easy to understand.

Use this structure:

# Introduction

Give a concise introduction based only on the research.

# What Is It?

Explain the definition using information explicitly supported
by the research.

# How It Works

Explain the process step by step using only supported information.

# Key Components

Explain the important components and their roles.

# Practical Example

Use ONLY practical examples found in the research.

# Benefits

List benefits explicitly supported by the research.

# Limitations

List limitations or challenges explicitly supported by the research.

# Technical Details

Include technical details explicitly supported by the research.

# Conclusion

Summarize the report without introducing new information.

# Sources

List ONLY the exact URLs from Verified Sources.

Output each URL exactly as provided.
"""
    ),
    (
        "human",
        """
Topic:
{topic}

Research Gathered:
{research}

Verified Sources:
{sources}

Write the final research report.
"""
    )
])

writer_chain = writer_prompt | llm | StrOutputParser()


# -------------------------
# CRITIC
# -------------------------

critic_prompt = ChatPromptTemplate([
    (
        "system",
        """
You are a strict but constructive research critic.

Check whether the report is:

- Accurate
- Well structured
- Sufficiently detailed
- Technically useful
- Supported by the provided research
- Free from unsupported claims
- Using the verified sources correctly
"""
    ),
    (
        "human",
        """
Review this research report:

{report}

Respond exactly in this format:

Score: X/10

Strengths:
- ...
- ...

Weaknesses:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
"""
    )
])

critic_chain = critic_prompt | llm | StrOutputParser()
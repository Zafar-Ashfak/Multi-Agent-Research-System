<h1>ResearchForge AI – Multi-Agent Research System</h1>
<br />

<p>
ResearchForge AI is a multi-agent research system designed to provide accurate and research-based answers to user queries. It uses web search to find relevant sources, scrapes useful information from selected websites, and uses AI agents to generate and review the final response. The system includes a <strong>Web Search Tool</strong>, <strong>Reader Agent</strong>, <strong>Writer Agent</strong>, and <strong>Critic Agent</strong> to create a complete research workflow. It also provides a clean Streamlit interface with chat history, source links, raw research results, critic feedback, and downloadable research reports.
</p>

<br />

<h2>Features</h2>

<ul>
<li>AI-powered web research</li>
<li>Real-time web search using Tavily</li>
<li>Web scraping using Requests and BeautifulSoup</li>
<li>Multi-agent research workflow</li>
<li>Research Writer Agent for generating reports</li>
<li>Critic Agent for reviewing accuracy and quality</li>
<li>Source URLs and scraped content</li>
<li>ChatGPT-style Streamlit interface</li>
<li>Dark and Light mode</li>
<li>Download research reports in Markdown format</li>
</ul>

<br />

<h2>How It Works</h2>

<p>
The user enters a research topic, and the system first searches the web using Tavily. It then selects the top sources and extracts useful information from those websites. The Writer Agent uses the collected research to generate the final answer, while the Critic Agent reviews the response for accuracy, relevance, source quality, and unsupported claims.
</p>

<br />

<br />

<h2>Workflow</h2>

<pre>
                                     ┌──────────────────────┐
                                     │     User Query       │
                                     │   Research Topic     │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │     Web Search       │
                                     │     Tavily API       │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │   Top 3 Sources      │
                                     │    URL Selection     │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │    Web Scraping      │
                                     │ Requests + Beautiful │
                                     │        Soup          │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │  Research Content    │
                                     │ Search + Scraped Data│
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │    Writer Agent      │
                                     │  GPT-OSS-120B +      │
                                     │      LangChain       │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │   Research Report    │
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                     ┌──────────────────────┐
                                     │     Critic Agent     │
                                     │ Accuracy + Sources + │
                                     │   Hallucination Check│
                                     └──────────┬───────────┘
                                                │
                                                ▼
                                ┌──────────────────────────────┐
                                │        Final Output          │
                                │ Report │ Sources │ Feedback  │
                                └──────────────┬───────────────┘
                                               │
                                               ▼
                                     ┌──────────────────────┐
                                     │  Streamlit Interface │
                                     │  View + Download MD  │
                                     └──────────────────────┘
</pre>

<br />

<br />

<h2>Tech Stack</h2>

<strong>Language:</strong> Python
<br/>
<strong>AI Framework:</strong> LangChain
<br/>
<strong>LLM:</strong> Hugging Face – GPT-OSS-120B
<br/>
<strong>Web Search:</strong> Tavily API
<br/>
<strong>Web Scraping:</strong> Requests and BeautifulSoup
<br/>
<strong>Frontend:</strong> Streamlit
<br/>
<strong>Environment Management:</strong> python-dotenv
<br/>
<strong>Tools & Platforms:</strong> Git, GitHub, VS Code

<br />
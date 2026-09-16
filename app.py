"""
Streamlit UI for the Multi-Agent Research System.

Drop this file into the same folder as agents.py, pipeline.py, and tools.py,
then run:

    streamlit run streamlit_app.py

It reuses extract_urls() from pipeline.py and the same chains/tools from
agents.py / tools.py, but drives them step-by-step so the UI can show live
progress instead of only printing to the terminal.
"""

import streamlit as st

from pipeline import extract_urls
from agents import writer_chain, critic_chain
from tools import web_search, scrape_url


# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="ResearchForge AI",
    page_icon="🔎",
    layout="wide",
)

if "result" not in st.session_state:
    st.session_state.result = None
if "running" not in st.session_state:
    st.session_state.running = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"


# ======================================================
# THEME (light / dark toggle)
# ======================================================

LIGHT_THEME = {
    "bg": "#ffffff",
    "secondary_bg": "#f5f6f8",
    "text": "#1a1a1a",
    "card": "#ffffff",
    "border": "#e0e2e6",
}

DARK_THEME = {
    "bg": "#0e1117",
    "secondary_bg": "#161a23",
    "text": "#f2f2f2",
    "card": "#1c212c",
    "border": "#2b3140",
}


def inject_theme_css(theme: dict) -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme["bg"]};
            color: {theme["text"]};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {theme["secondary_bg"]};
        }}
        div[data-testid="stTextArea"] textarea {{
            background-color: {theme["card"]};
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
        }}
        div[data-testid="stStatus"], div[data-testid="stExpander"] {{
            background-color: {theme["card"]};
            border: 1px solid {theme["border"]};
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {theme["text"]};
        }}
        h1, h2, h3, h4, p, label, span {{
            color: {theme["text"]};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme_css(DARK_THEME if st.session_state.theme == "dark" else LIGHT_THEME)


# ======================================================
# PIPELINE RUNNER (mirrors pipeline.run_research_pipeline,
# but reports progress back to the UI at each step)
# ======================================================

def run_pipeline_with_ui(topic: str) -> dict:
    state = {}

    # --- STEP 1: WEB SEARCH -----------------------------------------
    with st.status("Step 1/4 · Searching the web...", expanded=True) as status:
        state["search_results"] = web_search.invoke({"query": topic})
        st.write(f"Search complete for **{topic}**.")
        status.update(label="Step 1/4 · Web search complete", state="complete")

    # --- STEP 2: SELECT + SCRAPE SOURCES ------------------------------
    with st.status("Step 2/4 · Reading top sources...", expanded=True) as status:
        urls = extract_urls(state["search_results"])

        if not urls:
            status.update(label="Step 2/4 · No sources found", state="error")
            raise ValueError("No URLs were found in the search results.")

        selected_urls = urls[:3]
        scraped_sources = []

        for index, url in enumerate(selected_urls, start=1):
            st.write(f"Reading source {index}/{len(selected_urls)}: {url}")
            content = scrape_url.invoke({"url": url})
            scraped_sources.append(
                f"\nSOURCE {index}\nURL: {url}\n\nCONTENT:\n{content}\n"
            )

        state["scraped_content"] = "\n\n" + "\n\n".join(scraped_sources)
        state["sources"] = selected_urls
        status.update(label="Step 2/4 · Sources read", state="complete")

    # --- STEP 3: WRITER ------------------------------------------------
    with st.status("Step 3/4 · Writer is drafting the report...", expanded=True) as status:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        state["research_combined"] = research_combined
        status.update(label="Step 3/4 · Draft report ready", state="complete")

    # --- STEP 4: CRITIC --------------------------------------------------
    with st.status("Step 4/4 · Critic is reviewing the report...", expanded=True) as status:
        state["feedback"] = critic_chain.invoke({
            "topic": topic,
            "research": state["research_combined"],
            "report": state["report"],
        })
        status.update(label="Step 4/4 · Review complete", state="complete")

    return state


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.header("🔎 Research System")
    st.caption(
        "A multi-agent pipeline that searches the web, reads the top "
        "sources, drafts a report, and has it critiqued — all automatically."
    )
    st.divider()
    st.markdown(
        "**Pipeline steps**\n"
        "1. Web search\n"
        "2. Scrape top 3 sources\n"
        "3. Writer drafts report\n"
        "4. Critic reviews report"
    )


# ======================================================
# MAIN
# ======================================================

def _get_text(x):
    """writer_chain/critic_chain may return a string or an object with .content"""
    return getattr(x, "content", x)


title_col_left, title_col_center, title_col_right = st.columns([1, 6, 1])

with title_col_center:
    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>ResearchForge AI</h1>",
        unsafe_allow_html=True,
    )

with title_col_right:
    toggle_icon = "🌙" if st.session_state.theme == "light" else "☀️"
    if st.button(toggle_icon, key="theme_toggle", help="Toggle dark / light mode"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

with st.form("research_form"):
    topic = st.text_area(
        "Research topic",
        placeholder="e.g. Impact of AI on renewable energy adoption",
        height=160,
    )
    btn_col_left, btn_col_right = st.columns([5, 1])
    with btn_col_right:
        submitted = st.form_submit_button("Run Research", type="primary")

if submitted:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        st.session_state.running = True
        try:
            st.session_state.result = run_pipeline_with_ui(topic.strip())
            st.session_state.result["topic"] = topic.strip()
        except Exception as e:
            st.error(f"The pipeline failed: {e}")
            st.session_state.result = None
        finally:
            st.session_state.running = False

# ======================================================
# RESULTS
# ======================================================

result = st.session_state.result

if result:
    st.divider()
    st.subheader(f"Results for: {result['topic']}")

    report_text = _get_text(result["report"])
    feedback_text = _get_text(result["feedback"])

    tab_report, tab_feedback, tab_sources, tab_raw = st.tabs(
        ["📄 Report", "🧐 Critic Feedback", "🔗 Sources", "🗒️ Raw Search Results"]
    )

    with tab_report:
        st.markdown(report_text)
        st.download_button(
            "Download report (.md)",
            data=report_text,
            file_name=f"{result['topic'].replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tab_feedback:
        st.markdown(feedback_text)

    with tab_sources:
        for i, url in enumerate(result.get("sources", []), start=1):
            st.markdown(f"**Source {i}:** [{url}]({url})")
        with st.expander("View scraped content"):
            st.text(result["scraped_content"])

    with tab_raw:
        st.text(result["search_results"])
else:
    st.info("Enter a topic above and click **Run Research** to get started.")
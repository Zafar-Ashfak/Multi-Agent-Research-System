"""
ResearchForge AI — Streamlit UI

Run:
    streamlit run streamlit_app.py
"""

import streamlit as st

from pipeline import extract_urls
from agents import writer_chain, critic_chain
from tools import web_search, scrape_url


# ======================================================
# PAGE CONFIG & STATE
# ======================================================

st.set_page_config(
    page_title="ResearchForge AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state.setdefault("messages", [])
st.session_state.setdefault("theme", "dark")


# ======================================================
# THEME
# ======================================================

DARK = {
    "bg": "#000000",
    "text": "#ececec",
    "muted": "#9b9b9b",
    "bubble": "#2f2f2f",
    "card": "#161616",
    "border": "#1f1f1f",
    "hover": "#171717",
    "input": "#212121",
}

LIGHT = {
    "bg": "#ffffff",
    "text": "#0d0d0d",
    "muted": "#6e6e80",
    "bubble": "#f4f4f4",
    "card": "#ffffff",
    "border": "#e5e5e5",
    "hover": "#ececec",
    "input": "#f4f4f4",
}


def apply_theme():
    t = DARK if st.session_state.theme == "dark" else LIGHT

    st.markdown(
        f"""
        <style>
        html, body, .stApp {{
            font-family: -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
        }}

        .stApp, section[data-testid="stSidebar"] {{
            background: {t["bg"]} !important;
            color: {t["text"]} !important;
        }}

        .main .block-container {{
            max-width: 48rem;
            padding-top: 2.5rem;
            padding-bottom: 9rem;
            margin: auto;
        }}

        section[data-testid="stSidebar"] {{
            border-right: 1px solid {t["border"]};
        }}

        section[data-testid="stSidebar"] * {{
            color: {t["text"]} !important;
        }}

        section[data-testid="stSidebar"] button {{
            background: transparent !important;
            border: none !important;
            border-radius: 10px !important;
            text-align: left;
        }}

        section[data-testid="stSidebar"] button:hover {{
            background: {t["hover"]} !important;
        }}

        h1, h2, h3, h4, p, label, span {{
            color: {t["text"]};
        }}

        .rf-header {{
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            font-size: 1.05rem;
            padding: .25rem .1rem .75rem;
        }}

        .rf-empty {{
            text-align: center;
            margin-top: 22vh;
            font-size: 2rem;
            font-weight: 500;
        }}

        div[data-testid="stChatMessage"] {{
            background: transparent !important;
            border: none !important;
            padding: .75rem 0 !important;
        }}

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarUser"]
        ) {{
            display: flex;
            flex-direction: row-reverse;
        }}

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarUser"]
        ) div[data-testid="stChatMessageContent"] {{
            background: {t["bubble"]} !important;
            border-radius: 20px;
            padding: .65rem 1.1rem;
            max-width: 70%;
        }}

        div[data-testid="stChatMessageAvatarUser"] {{
            display: none;
        }}

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarAssistant"]
        ) div[data-testid="stChatMessageContent"] {{
            background: transparent !important;
            max-width: 100%;
        }}

        div[data-testid="stChatMessageAvatarAssistant"] {{
            background: #10a37f !important;
            border-radius: 50%;
        }}

        /* ChatGPT-style composer */
        div[data-testid="stBottom"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stChatInput"] {{
            max-width: 48rem;
            margin: auto;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stChatInput"] > div,
        div[data-testid="stChatInput"] form,
        div[data-testid="stChatInput"] [data-baseweb="textarea"],
        div[data-testid="stChatInput"] [data-baseweb="base-input"] {{
            background: {t["input"]} !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            border-radius: 28px !important;
        }}

        div[data-testid="stChatInput"] textarea {{
            background: {t["input"]} !important;
            color: {t["text"]} !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            border-radius: 28px !important;
            padding: 14px 58px 14px 18px !important;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            color: {t["muted"]} !important;
        }}

        div[data-testid="stChatInput"]:focus-within,
        div[data-testid="stChatInput"] *:focus,
        div[data-testid="stChatInput"] *:focus-within {{
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stChatInput"] button {{
            background: {t["muted"]} !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 50% !important;
        }}

        div[data-testid="stChatInput"] button:hover {{
            background: {t["text"]} !important;
        }}

        div[data-testid="stStatus"],
        div[data-testid="stExpander"] {{
            background: {t["card"]};
            border: 1px solid {t["border"]};
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme()


# ======================================================
# PIPELINE
# ======================================================

def run_pipeline(topic):
    with st.status("Searching the web...", expanded=True) as status:
        results = web_search.invoke({"query": topic})
        status.update(label="Web search complete", state="complete")

    with st.status("Reading top sources...", expanded=True) as status:
        urls = extract_urls(results)

        if not urls:
            raise ValueError("No URLs were found in the search results.")

        sources = urls[:3]
        scraped = []

        for i, url in enumerate(sources, 1):
            st.write(f"Reading source {i}/{len(sources)}: {url}")
            content = scrape_url.invoke({"url": url})
            scraped.append(f"SOURCE {i}\nURL: {url}\n\n{content}")

        scraped_content = "\n\n".join(scraped)
        status.update(label="Sources read", state="complete")

    research = (
        f"SEARCH RESULTS:\n{results}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{scraped_content}"
    )

    with st.status("Drafting the report...", expanded=True) as status:
        report = writer_chain.invoke({
            "topic": topic,
            "research": research,
        })
        status.update(label="Draft report ready", state="complete")

    with st.status("Critic is reviewing...", expanded=True) as status:
        feedback = critic_chain.invoke({
            "topic": topic,
            "research": research,
            "report": report,
        })
        status.update(label="Review complete", state="complete")

    return {
        "topic": topic,
        "report": getattr(report, "content", report),
        "feedback": getattr(feedback, "content", feedback),
        "sources": sources,
        "scraped_content": scraped_content,
        "search_results": results,
    }


# ======================================================
# RESULT
# ======================================================

def render_result(result):

    report, feedback = result["report"], result["feedback"]

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📄 Report", "🧐 Critic Feedback", "🔗 Sources", "🗒️ Raw Results"]
    )

    with tab1:
        st.markdown(report)
        st.download_button(
            "Download report (.md)",
            report,
            file_name=f"{result['topic'].replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with tab2:
        st.markdown(feedback)

    with tab3:
        for i, url in enumerate(result["sources"], 1):
            st.markdown(f"**Source {i}:** [{url}]({url})")

        with st.expander("View scraped content"):
            st.text(result["scraped_content"])

    with tab4:
        st.text(result["search_results"])


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:

    st.markdown(
        """
        <div class="rf-header">
            <span>🔎 ResearchForge AI</span>
            <span>🔍 ⤢</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("✏️  New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Chats")

    topics = [
        m["topic"]
        for m in st.session_state.messages
        if m["role"] == "user"
    ]

    if topics:
        for i, topic in enumerate(reversed(topics)):
            label = topic if len(topic) <= 34 else topic[:31] + "..."
            st.button(
                label,
                use_container_width=True,
                disabled=True,
                key=f"history_{i}",
            )
    else:
        st.caption("No chats yet")

    st.write("")

    icon = "☀️" if st.session_state.theme == "dark" else "🌙"

    if st.button(icon, key="theme_toggle"):
        st.session_state.theme = (
            "light"
            if st.session_state.theme == "dark"
            else "dark"
        )
        st.rerun()


# ======================================================
# CHAT
# ======================================================

if not st.session_state.messages:

    st.markdown(
        '<div class="rf-empty">What\'s on your mind today?</div>',
        unsafe_allow_html=True,
    )

else:

    for message in st.session_state.messages:

        if message["role"] == "user":

            with st.chat_message("user"):
                st.markdown(message["topic"])

        else:

            with st.chat_message("assistant", avatar="✨"):

                if message.get("error"):
                    st.error(
                        f"The pipeline failed: {message['error']}"
                    )
                else:
                    render_result(message["result"])


# ======================================================
# INPUT
# ======================================================

if prompt := st.chat_input("Ask anything"):

    topic = prompt.strip()

    if topic:

        st.session_state.messages.append({
            "role": "user",
            "topic": topic,
        })

        with st.chat_message("user"):
            st.markdown(topic)

        with st.chat_message("assistant", avatar="✨"):

            try:
                result = run_pipeline(topic)
                render_result(result)

                st.session_state.messages.append({
                    "role": "assistant",
                    "result": result,
                })

            except Exception as e:

                st.error(f"The pipeline failed: {e}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "error": str(e),
                })
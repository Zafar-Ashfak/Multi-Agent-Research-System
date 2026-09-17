"""
ResearchForge AI
----------------
Streamlit UI for the Multi-Agent Research System.

Project files:
    app.py
    agents.py
    pipeline.py
    tools.py

Run:
    streamlit run app.py
"""

import streamlit as st

from agents import writer_chain, critic_chain
from pipeline import extract_urls
from tools import web_search, scrape_url

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchForge AI",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================

st.session_state.setdefault("messages", [])
st.session_state.setdefault("theme", "dark")

# ============================================================
# THEME CONFIGURATION
# ============================================================

DARK_THEME = {
    "background": "#000000",
    "sidebar": "#000000",
    "text": "#ececec",
    "muted": "#9b9b9b",
    "input": "#212121",
    "bubble": "#2f2f2f",
    "card": "#161616",
    "border": "#1f1f1f",
    "hover": "#171717",
    "link": "#4da3ff",
}

LIGHT_THEME = {
    "background": "#ffffff",
    "sidebar": "#ffffff",
    "text": "#0d0d0d",
    "muted": "#6e6e80",
    "input": "#f4f4f4",
    "bubble": "#f4f4f4",
    "card": "#ffffff",
    "border": "#e5e5e5",
    "hover": "#ececec",
    "link": "#1683e8",
}


def get_theme():
    """Return the currently selected theme."""
    return (
        DARK_THEME
        if st.session_state.theme == "dark"
        else LIGHT_THEME
    )


# ============================================================
# CUSTOM CSS
# ============================================================

def apply_css():
    """Apply application-wide theme and UI styling."""

    theme = get_theme()

    st.markdown(
        f"""
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        html,
        body,
        .stApp {{
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Helvetica,
                Arial,
                sans-serif;
        }}

        .stApp {{
            background-color: {theme["background"]} !important;
            color: {theme["text"]} !important;
        }}

        .main .block-container {{
            max-width: 48rem;
            margin: 0 auto;
            padding-top: 2.5rem;
            padding-bottom: 9rem;
        }}

        h1,
        h2,
        h3,
        h4,
        h5,
        h6,
        p,
        label,
        span,
        li {{
            color: {theme["text"]} !important;
        }}


        /* ==================================================
           SIDEBAR
           ================================================== */

        section[data-testid="stSidebar"] {{
            background-color: {theme["sidebar"]} !important;
            border-right: 1px solid {theme["border"]} !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: {theme["text"]} !important;
        }}

        section[data-testid="stSidebar"] button {{
            background: transparent !important;
            border: none !important;
            border-radius: 10px !important;
            text-align: left !important;
        }}

        section[data-testid="stSidebar"] button:hover {{
            background: {theme["hover"]} !important;
        }}

        section[data-testid="stSidebar"] button:disabled {{
            opacity: 0.7 !important;
        }}

        .rf-sidebar-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;

            padding:
                0.25rem
                0.1rem
                0.75rem;

            font-size: 1.05rem;
            font-weight: 600;
        }}

        .rf-sidebar-icons {{
            color: {theme["muted"]} !important;
        }}


        /* ==================================================
           EMPTY CHAT STATE
           ================================================== */

        .rf-empty {{
            display: flex;
            justify-content: center;
            align-items: center;

            margin-top: 22vh;

            text-align: center;

            color: {theme["text"]};

            font-size: 2rem;
            font-weight: 500;
        }}


        /* ==================================================
           CHAT MESSAGES
           ================================================== */

        div[data-testid="stChatMessage"] {{
            background: transparent !important;
            border: none !important;
            padding: 0.75rem 0 !important;
        }}

        /* User message */

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarUser"]
        ) {{
            display: flex;
            flex-direction: row-reverse;
        }}

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarUser"]
        )
        div[data-testid="stChatMessageContent"] {{
            background-color: {theme["bubble"]} !important;

            border-radius: 20px !important;

            padding:
                0.65rem
                1.1rem !important;

            max-width: 70% !important;
        }}

        div[data-testid="stChatMessageAvatarUser"] {{
            display: none !important;
        }}

        /* Assistant message */

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarAssistant"]
        ) {{
            margin-top: 24px !important;
        }}

        div[data-testid="stChatMessage"]:has(
            div[data-testid="stChatMessageAvatarAssistant"]
        ) div[data-testid="stChatMessageContent"] {{
            background: transparent !important;
            max-width: 100% !important;
        }}

        div[data-testid="stChatMessageAvatarAssistant"] {{
            background-color: #10a37f !important;
            border-radius: 50% !important;
        }}

        /* ==================================================
           CHATGPT-STYLE CHAT INPUT
           ================================================== */

        /*
         * Remove Streamlit bottom container styling.
         */

        div[data-testid="stBottom"] {{
            background: transparent !important;
            background-color: transparent !important;

            border: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="stBottom"] * {{
            box-shadow: none !important;
        }}


        /*
         * Main input wrapper.
         */

        div[data-testid="stChatInput"] {{
            max-width: 48rem;
            margin: 0 auto;

            background: transparent !important;
            background-color: transparent !important;

            border: none !important;
            outline: none !important;

            box-shadow: none !important;
        }}


        /*
         * Streamlit/BaseWeb input containers.
         */

        div[data-testid="stChatInput"] > div,
        div[data-testid="stChatInput"] form,
        div[data-testid="stChatInput"] [data-baseweb="textarea"],
        div[data-testid="stChatInput"] [data-baseweb="base-input"] {{
            background-color: {theme["input"]} !important;

            border: none !important;
            outline: none !important;

            box-shadow: none !important;

            border-radius: 28px !important;
        }}


        /*
         * Actual textarea.
         */

        div[data-testid="stChatInput"] textarea {{
            background-color: {theme["input"]} !important;

            color: {theme["text"]} !important;

            border: none !important;
            outline: none !important;

            box-shadow: none !important;

            border-radius: 28px !important;

            padding:
                14px
                58px
                14px
                18px !important;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            color: {theme["muted"]} !important;
            opacity: 1 !important;
        }}


        /*
         * Completely remove focus borders.
         */

        div[data-testid="stChatInput"]:focus,
        div[data-testid="stChatInput"]:focus-within,
        div[data-testid="stChatInput"] > div:focus,
        div[data-testid="stChatInput"] > div:focus-within,
        div[data-testid="stChatInput"] form:focus,
        div[data-testid="stChatInput"] form:focus-within,
        div[data-testid="stChatInput"] *:focus,
        div[data-testid="stChatInput"] *:focus-within {{
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }}


        /*
         * Send button.
         */

        div[data-testid="stChatInput"] button {{
            background-color: {theme["muted"]} !important;

            border: none !important;
            outline: none !important;

            box-shadow: none !important;

            border-radius: 50% !important;
        }}

        div[data-testid="stChatInput"] button:hover {{
            background-color: {theme["text"]} !important;
        }}


        /* ==================================================
           MARKDOWN / TEXT / RAW CONTENT
           ================================================== */

        /*
         * st.text() uses <pre>.
         * Explicitly set the text color so that
         * Raw Results and scraped content work
         * correctly in both themes.
         */

        div[data-testid="stText"],
        div[data-testid="stText"] pre,
        div[data-testid="stText"] pre *,
        pre,
        pre * {{
            color: {theme["text"]} !important;
            background: transparent !important;
        }}


        /*
         * Markdown content.
         */

        div[data-testid="stMarkdownContainer"],
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] strong {{
            color: {theme["text"]} !important;
        }}


        /*
         * Source links.
         */

        div[data-testid="stMarkdownContainer"] a {{
            color: {theme["link"]} !important;
        }}


        /* ==================================================
           EXPANDERS
           ================================================== */

        div[data-testid="stExpander"] {{
            background-color: {theme["card"]} !important;

            border:
                1px solid {theme["border"]} !important;

            border-radius: 12px !important;
        }}

        div[data-testid="stExpander"] * {{
            color: {theme["text"]} !important;
        }}

        div[data-testid="stExpander"] pre,
        div[data-testid="stExpander"] pre * {{
            color: {theme["text"]} !important;
            background: transparent !important;
        }}


        /* ==================================================
           STATUS
           ================================================== */

        div[data-testid="stStatus"] {{
            background-color: {theme["card"]} !important;

            border:
                1px solid {theme["border"]} !important;

            border-radius: 12px !important;
        }}

        div[data-testid="stStatus"] * {{
            color: {theme["text"]} !important;
        }}


        /* ==================================================
           TABS
           ================================================== */

        .stTabs [data-baseweb="tab"] {{
            color: {theme["text"]} !important;
        }}

        .stTabs [data-baseweb="tab"] * {{
            color: {theme["text"]} !important;
        }}

        .stTabs [aria-selected="true"] {{
            color: {theme["text"]} !important;
        }}


        /* ==================================================
           DOWNLOAD BUTTON
           ================================================== */

        .stDownloadButton button {{
            border:
                1px solid {theme["border"]} !important;

            background-color:
                {theme["card"]} !important;

            color:
                {theme["text"]} !important;
        }}


        /* ==================================================
           TOOLTIP
           ================================================== */

        div[data-baseweb="tooltip"],
        div[data-testid="stTooltipContent"],
        [role="tooltip"] {{
            color: #ffffff !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


apply_css()


# ============================================================
# RESEARCH PIPELINE
# ============================================================

def run_pipeline(topic: str) -> dict:
    """Run the complete research workflow."""

    # --------------------------------------------------------
    # 1. Web search
    # --------------------------------------------------------

    with st.status(
            "Searching the web...",
            expanded=True,
    ) as status:

        search_results = web_search.invoke(
            {"query": topic}
        )

        status.update(
            label="Web search complete",
            state="complete",
        )

    # --------------------------------------------------------
    # 2. Extract and scrape sources
    # --------------------------------------------------------

    with st.status(
            "Reading top sources...",
            expanded=True,
    ) as status:

        urls = extract_urls(search_results)

        if not urls:
            status.update(
                label="No sources found",
                state="error",
            )

            raise ValueError(
                "No URLs were found in the search results."
            )

        sources = urls[:3]
        scraped_sources = []

        for index, url in enumerate(sources, start=1):
            st.write(
                f"Reading source "
                f"{index}/{len(sources)}: {url}"
            )

            content = scrape_url.invoke(
                {"url": url}
            )

            scraped_sources.append(
                f"""
SOURCE {index}
URL: {url}

CONTENT:
{content}
"""
            )

        scraped_content = "\n\n".join(
            scraped_sources
        )

        status.update(
            label="Sources read",
            state="complete",
        )

    # --------------------------------------------------------
    # 3. Combine research
    # --------------------------------------------------------

    research = (
        f"SEARCH RESULTS:\n"
        f"{search_results}\n\n"
        f"DETAILED SCRAPED CONTENT:\n"
        f"{scraped_content}"
    )

    # --------------------------------------------------------
    # 4. Writer agent
    # --------------------------------------------------------

    with st.status(
            "Drafting the report...",
            expanded=True,
    ) as status:

        report = writer_chain.invoke(
            {
                "topic": topic,
                "research": research,
            }
        )

        report = getattr(
            report,
            "content",
            report,
        )

        status.update(
            label="Draft report ready",
            state="complete",
        )

    # --------------------------------------------------------
    # 5. Critic agent
    # --------------------------------------------------------

    with st.status(
            "Critic is reviewing...",
            expanded=True,
    ) as status:

        feedback = critic_chain.invoke(
            {
                "topic": topic,
                "research": research,
                "report": report,
            }
        )

        feedback = getattr(
            feedback,
            "content",
            feedback,
        )

        status.update(
            label="Review complete",
            state="complete",
        )

    return {
        "topic": topic,
        "report": report,
        "feedback": feedback,
        "sources": sources,
        "scraped_content": scraped_content,
        "search_results": search_results,
    }


# ============================================================
# RESULT RENDERING
# ============================================================

def render_result(result: dict) -> None:
    """Render report, feedback, sources and raw results."""

    report_tab, feedback_tab, sources_tab, raw_tab = st.tabs(
        [
            "📄 Report",
            "🧐 Critic Feedback",
            "🔗 Sources",
            "🗒️ Raw Results",
        ]
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    with report_tab:
        st.markdown(
            result["report"]
        )

        st.download_button(
            "Download report (.md)",
            data=result["report"],
            file_name=(
                f"{result['topic'].replace(' ', '_')}"
                "_report.md"
            ),
            mime="text/markdown",
            use_container_width=True,
            key=f"download_{id(result)}",
        )

    # --------------------------------------------------------
    # Critic feedback
    # --------------------------------------------------------

    with feedback_tab:
        st.markdown(
            result["feedback"]
        )

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    with sources_tab:
        for index, url in enumerate(
                result["sources"],
                start=1,
        ):
            st.markdown(
                f"**Source {index}:** "
                f"[{url}]({url})"
            )

        with st.expander(
                "View scraped content"
        ):
            st.text(
                result["scraped_content"]
            )

    # --------------------------------------------------------
    # Raw search results
    # --------------------------------------------------------

    with raw_tab:
        st.text(
            result["search_results"]
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="rf-sidebar-header">
            <span>🔎 ResearchForge AI</span>
            <span class="rf-sidebar-icons">
                🔍 &nbsp;⤢
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # New chat
    # --------------------------------------------------------

    if st.button(
            "✏️  New chat",
            use_container_width=True,
    ):
        st.session_state.messages = []

        st.rerun()

    st.markdown(
        '<div style="height:0.75rem"></div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Chat history
    # --------------------------------------------------------

    st.caption("Chats")

    topics = [
        message["topic"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]

    if topics:

        for index, topic in enumerate(
                reversed(topics)
        ):
            label = (
                topic
                if len(topic) <= 34
                else topic[:31] + "..."
            )

            st.button(
                label,
                use_container_width=True,
                disabled=True,
                key=f"history_{index}",
            )

    else:

        st.caption("No chats yet")

    # --------------------------------------------------------
    # Theme toggle
    # --------------------------------------------------------

    st.markdown(
        '<div style="height:2rem"></div>',
        unsafe_allow_html=True,
    )

    theme_icon = (
        "☀️"
        if st.session_state.theme == "dark"
        else "🌙"
    )

    # IMPORTANT:
    # Widget key must NOT be "theme"
    # because "theme" is used in session_state.

    if st.button(
            theme_icon,
            key="theme_toggle",
    ):
        st.session_state.theme = (
            "light"
            if st.session_state.theme == "dark"
            else "dark"
        )

        st.rerun()

# ============================================================
# CHAT HISTORY
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="rf-empty">
            What's on your mind today?
        </div>
        """,
        unsafe_allow_html=True,
    )


else:

    for message in st.session_state.messages:

        # ----------------------------------------------------
        # User message
        # ----------------------------------------------------

        if message["role"] == "user":

            with st.chat_message("user"):

                st.markdown(
                    message["topic"]
                )


        # ----------------------------------------------------
        # Assistant message
        # ----------------------------------------------------

        else:

            with st.chat_message(
                    "assistant",
                    avatar="✨",
            ):

                if message.get("error"):

                    st.error(
                        "The pipeline failed: "
                        f"{message['error']}"
                    )

                else:

                    render_result(
                        message["result"]
                    )

# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask anything"
)

# ============================================================
# PROCESS NEW PROMPT
# ============================================================

if prompt:

    topic = prompt.strip()

    if topic:

        # ----------------------------------------------------
        # Display user message
        # ----------------------------------------------------

        with st.chat_message("user"):

            st.markdown(topic)

        # ----------------------------------------------------
        # Run pipeline
        # ----------------------------------------------------

        with st.chat_message(
                "assistant",
                avatar="✨",
        ):

            try:

                result = run_pipeline(
                    topic
                )

                render_result(
                    result
                )

                # Save conversation
                st.session_state.messages.extend(
                    [
                        {
                            "role": "user",
                            "topic": topic,
                        },
                        {
                            "role": "assistant",
                            "result": result,
                        },
                    ]
                )


            except Exception as error:

                st.error(
                    f"The pipeline failed: {error}"
                )

                st.session_state.messages.extend(
                    [
                        {
                            "role": "user",
                            "topic": topic,
                        },
                        {
                            "role": "assistant",
                            "error": str(error),
                        },
                    ]
                )

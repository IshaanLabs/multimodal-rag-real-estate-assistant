import os
import requests
import streamlit as st
from streamlit_chat import message

def get_api_url():
    try:
        return st.secrets["API_URL"]
    except Exception:
        return os.environ.get("API_URL", "http://localhost:8000")

API_URL = get_api_url()

def chat(message_text, session_id):
    r = requests.post(
        f"{API_URL}/chat",
        json={"message": message_text, "session_id": session_id, "context": {}},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()

st.set_page_config(page_title="Al Badia Villas RAG", page_icon="🏠", layout="wide")

st.title("Al Badia Villas Conversational Assistant")
st.subheader("RAG-powered answers with floorplans, citations, and lead insights")

with st.sidebar:
    st.header("Controls")
    default_sid = st.session_state.get("session_id", "demo")
    session_id = st.text_input("Session ID", value=default_sid)
    st.session_state["session_id"] = session_id
    if st.button("Reset session"):
        st.session_state.clear()
        st.rerun()
    show_images = st.checkbox("Show images", value=True)
    show_citations = st.checkbox("Show citations", value=True)
    show_leads = st.checkbox("Show lead insights", value=True)
    st.markdown(f"API: `{API_URL}`")
    st.markdown("---")
    st.markdown(
        "**About**\n\nThis assistant answers questions about Al Badia Villas using a RAG pipeline, "
        "shows floorplans, and highlights lead signals."
    )
    if st.button("Learn more"):
        st.session_state["show_about"] = True

if st.session_state.get("show_about"):
    st.info(
        "Retrieval-augmented chatbot for Al Badia Villas."
        "It ingests the floorplan PDF, chunks and embeds it into FAISS, retrieves the most relevant specs, and uses OpenAI to answer with citations and floorplan images. Built-in lead analysis highlights intent signals and suggests the next action."
    )
    st.session_state["show_about"] = False

if "history" not in st.session_state:
    st.session_state["history"] = []

# Process pending follow-up if any
pending = st.session_state.pop("pending_prompt", None)
if pending:
    st.session_state["history"].append(("user", pending))
    with st.spinner("⏳ Working on that follow-up…"):
        try:
            resp = chat(pending, session_id)
        except Exception as e:
            st.error(f"Request failed: {e}")
            resp = None
    if resp:
        st.session_state["history"].append(("assistant", resp))

# Always show chat input
prompt = st.chat_input("Ask about villas...")
if prompt:
    st.session_state["history"].append(("user", prompt))
    with st.spinner("⏳ Finding the best villas for you…"):
        try:
            resp = chat(prompt, session_id)
        except Exception as e:
            st.error(f"Request failed: {e}")
            resp = None
    if resp:
        st.session_state["history"].append(("assistant", resp))

# Render chat history with streamlit-chat bubbles
for idx, (role, content) in enumerate(st.session_state["history"]):
    if role == "user":
        message(content, is_user=True, key=f"user_{idx}", avatar_style="thumbs")
        continue

    # Assistant bubble
    message(content.get("response", ""), is_user=False, key=f"bot_{idx}", avatar_style="bottts")

    # Images (toggleable)
    imgs = content.get("images") or []
    if show_images and imgs:
        with st.expander("Images", expanded=True):
            cols = st.columns(min(3, len(imgs)))
            for col, img in zip(cols, imgs):
                url = img.get("path", "")
                if url.startswith("/"):
                    url = f"{API_URL}{url}"
                col.image(url, caption=img.get("description", ""), use_container_width=True)

    # Lead signals
    if show_leads and content.get("lead_signals"):
        ls = content["lead_signals"]
        contact = ls.get("contact_info") or {}
        with st.expander("Lead insights", expanded=True):
            st.markdown(
                f"- Intent: **{ls.get('intent', 'n/a')}**\n"
                f"- Signals: {', '.join(ls.get('signals_detected', [])) or 'none'}\n"
                f"- Recommended action: `{ls.get('recommended_action', 'n/a')}`"
            )
            if contact:
                parts = []
                if contact.get("email"):
                    parts.append(f"Email: {contact['email']}")
                if contact.get("phone"):
                    parts.append(f"Phone: {contact['phone']}")
                if contact.get("name"):
                    parts.append(f"Name: {contact['name']}")
                if parts:
                    st.markdown(f"- Contact: {' | '.join(parts)}")

    # Citations
    if show_citations and content.get("citations"):
        with st.expander("Citations"):
            for c in content["citations"]:
                st.markdown(
                    f"- chunk {c.get('chunk_index')} "
                    f"(score {c.get('relevance_score', 0):.2f}): "
                    f"{c.get('content_preview', '')}"
                )

    # Follow-up button: prefills & auto-sends next turn
    if content.get("follow_up_prompt"):
        follow = content["follow_up_prompt"]
        st.caption(f"Follow-up: {follow}")
        # if st.button("Use follow-up", key=f"follow_{idx}"):
        #     st.session_state["pending_prompt"] = follow
        #     st.rerun()


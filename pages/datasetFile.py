import streamlit as st

st.set_page_config(
    page_title="Genii • Conversation Analysis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.page_link("main.py", label="Introduction", icon="✨")
    st.page_link("pages/projectConversations.py", label="Project Conversations", icon="🔮")
    st.page_link("pages/conversation.py", label="Conversation", icon="💬")
    st.page_link("pages/datasetFile.py", label="Dataset File", icon="📄")

TOLKAI_LOGO = "Genii.svg"
st.logo(TOLKAI_LOGO)

st.title('🔮 :violet[Genii] • Conversation Analysis')
st.header("Dataset File Analysis")
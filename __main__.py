import streamlit as st


st.set_page_config(
    page_title="Genii • Conversation Analysis",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.page_link("__main__.py", label="Introduction", icon="🧞")
    st.page_link("pages/projectConversations.py", label="Project Conversations", icon="🔮")
    st.page_link("pages/conversation.py", label="Conversation", icon="💬")
    st.page_link("pages/datasetFile.py", label="Dataset File", icon="📄")
    st.page_link("pages/help.py", label="Help Center", icon="🛟")

TOLKAI_LOGO = "Genii.svg"
st.logo(TOLKAI_LOGO)

st.title('🧞 :violet[Genii] • Conversation Analysis')

st.markdown('''Welcome to **Conversation Analysis**, your go-to application for comprehensive conversation analysis. This powerful tool leverages artificial intelligence to extract and structure detailed insights from professional-client conversations, helping you understand and improve your communication dynamics.

## Project Overview

### What is Conversation Analysis?

Conversation Analysis is an AI-driven platform designed to analyze conversations and provide structured data insights. Whether you're a business looking to enhance customer service quality or a professional seeking to understand client interactions better, Conversation Analysis offers a robust solution to meet your needs.

### Key Features

- 🔎 **In-depth Analysis:** Extracts crucial insights beyond the surface-level conversation.
- 🥳 **Emotion and Sentiment Detection:** Identifies emotions and sentiment to gauge client satisfaction.
- 📈 **Service Quality Evaluation:** Assesses the quality of service provided based on the conversation.
- 📊 **Insightful Reporting:** Provides structured data in a JSON format for easy integration and analysis.''')
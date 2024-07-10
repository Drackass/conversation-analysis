import streamlit as st

def sidebar(page_title, title, header):

    st.set_page_config(
        page_title=page_title,
        page_icon="🧞",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    with st.sidebar:
        st.page_link("__main__.py", label="Introduction", icon="🧞")
        st.page_link("pages/projectConversations.py", label="Project Conversations", icon="🔮")
        st.page_link("pages/conversation.py", label="Conversation", icon="💬")
        st.page_link("pages/datasetFile.py", label="Dataset File", icon="📄")
        # st.page_link("pages/customDataset.py", label="Custom Dataset", icon="📝")
        st.page_link("pages/help.py", label="Help Center", icon="🛟")
        st.page_link("pages/filterTest.py", label="Filter", icon="🔍")

    TOLKAI_LOGO = "genii.svg"
    st.logo(TOLKAI_LOGO)

    st.title(title)
    st.header(header)
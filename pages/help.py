import streamlit as st

st.set_page_config(
    page_title="Genii • Conversation Analysis | Help Center",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.page_link("main.py", label="Introduction", icon="🧞")
    st.page_link("pages/projectConversations.py", label="Project Conversations", icon="🔮")
    st.page_link("pages/conversation.py", label="Conversation", icon="💬")
    st.page_link("pages/datasetFile.py", label="Dataset File", icon="📄")
    st.page_link("pages/help.py", label="Help Center", icon="🛟")


TOLKAI_LOGO = "Genii.svg"
st.logo(TOLKAI_LOGO)

st.title('🧞 :violet[Genii] • Conversation Analysis')
st.header("🛟 Help Center")

st.markdown('''
Welcome to the **Help Center**! Here, you'll find detailed information on how to use the **Conversation Analysis** application. Whether you're new to the platform or looking to explore advanced features, this guide will help you navigate through the application with ease.

## Getting Started

### 1. **Project Conversations**
- Navigate to the **Project Conversations** tab to view all conversations within a specific project.
- Select a user from the dropdown menu to view their conversations.
- Click on a conversation to analyze its details.

### 2. **Conversation Analysis**
- Enter a conversation ID to analyze a specific conversation.
- Customize the prompt to generate detailed insights based on your requirements.
- Select a model to analyze the conversation using different AI models.

### 3. **Dataset File Analysis**
- Upload a dataset file to analyze multiple conversations at once.
- Customize the prompt to generate detailed insights based on your requirements.
- Select a model to analyze the conversations using different AI models.
            
### 4. **Help Center**
- Explore this section to access detailed information on using the application.
- Learn about the key features, functionalities, and tools available in the application.
- Get step-by-step guidance on how to navigate through the application.   
            
### 5.Insights Entities
- **Boxes**: Extract crucial insights beyond the surface-level conversation.
    - **icon**: (emoji)
    - **label**: (string)
    - **value**: (string e.g."Extract crucial insights beyond the surface-level conversation.")
    - **type**: ("info"|"success"|"warning"|"error")
- **Metrics**: Identify emotions and sentiment to gauge client satisfaction.
    - **name**: (string)
    - **value**: (string e.g."positive"|"constructive"|"negative"|"neutral")
    - **delta**: (average number between -100 and 100)
- **Progress**: Assess the quality of service provided based on the conversation.
    - **name**: (string)
    - **value**: (string e.g."Very Poor"|"Poor"|"Fair"|"Good"|"Excellent")
    - **delta**: (average number between 0 and 100
            
### 6. **Supported File Formats**
- **CSV**: The application supports CSV file formats for uploading conversation datasets. Ensure that your dataset is in CSV format before uploading it to the platform.

| role | message |
| :------------ | :------------ |
| user | dummyUserMessage |
| assistant | dummyAssistantMessage |
''')
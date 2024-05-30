import datetime
from io import StringIO
import time
from turtle import pd
import numpy as np
import openai
import streamlit as st
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.bcolors import bcolors
from src.prompts import prompts
from src.routes import getConversationById, getConversationsByProjectId, sendMessageToLlm
from src.utils import extract_json_object, filter_insights
from src.pages.projectConversations import projectConversationsPage

st.set_page_config(
    page_title="Tolk.ai • Conversation Analysis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This is a dashboard to analyze conversations from Tolk.ai."
    }
)

st.title('🔮 :violet[Tolk.ai] • Conversation Analysis')

ProjectConversationsTab, ConversationTab, DatasetFileTab = st.tabs(["🤖 Project Conversations", "💬 Conversation", "📄 Dataset File"])

with ProjectConversationsTab:
    projectConversationsPage()
            

with ConversationTab:
    st.header("Conversation Analysis")
    projectId = st.text_input("Enter a ConversationId:", "e51255e3-2790-4ab7-964c-6f898f7e00f7")


with DatasetFileTab:
    st.header("Dataset File Analysis")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)
    # info for the structure of the file to be uploaded
    st.info('The file should be a **csv** file with the following structure: _user/agent : message_', icon='📄')



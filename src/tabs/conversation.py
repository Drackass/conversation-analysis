import streamlit as st

from src.routes import getAllUsers

def conversationTab():
    st.header("Conversation Analysis")


    allUsers = getAllUsers()

    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]
    
    projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversation")["id"]

    conversationId = st.text_input("Enter the conversation ID:", value="e51255e3-2790-4ab7-964c-6f898f7e00f7")

    return projectId, conversationId

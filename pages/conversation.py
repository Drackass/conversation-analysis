import pandas as pd
import streamlit as st
from src.routes import getAllUsers
from src.routes import getConversationById
from src.utils import flatten_json, extract_json_structure, formalize_messages
from src.prompts import prompts, context, jsonStructurePrompt
import openai
from src.components.sidebar import sidebar
import json

from src.misc import llmJson

sidebar("Genii • Conversation Analysis | Conversation",'🧞 :violet[Genii] • Conversation Analysis',"💬 Conversation Analysis")

try:
    allUsers = getAllUsers()
    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]   
except Exception as e:
    st.error(f"**Error Fetching all users** _(try to refresh the app)_", icon='❌')
    st.stop()

projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

conversationId = st.text_input("Enter the conversation ID:", "5a16bb08-8c87-4145-aaf5-2f75c7beb6f4")

customPrompt = st.text_area(
        label="Enter a prompt to analyze the conversations:",
        value=prompts[6],
        height=300,
    )

modelCol, analyzeCol = st.columns(2)

with modelCol:
    OpenAiApiModel = st.selectbox(
        "Select a model:",
        ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
        index=3,
        label_visibility="collapsed",
    )

with analyzeCol:
    btnAnalyze= st.button(
        "Analyze",
        use_container_width=True,
        type="primary",
        )
    
if btnAnalyze:
    st.divider()

    client = openai.OpenAI(
      api_key=st.secrets["OPENAI_API_KEY"],
    )

    error = ""
    analysis = st.empty()
    analysisResults = {}
    refJsonFormatPrompt = ""
    with analysis.status(f"🔎 1. {conversationId}", expanded=True) as status:
        st.write("analyzing conversation...")
        try:
            conversationMessages = getConversationById(projectId, conversationId)

            analysisPrompt = f"{context}\n{customPrompt}"
            if refJsonFormatPrompt:
                analysisPrompt += f"\n\n{refJsonFormatPrompt}"
            messages=[{"role": "system", "content": analysisPrompt}]
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    messages.append({"role": "assistant", "content": message["content"]["text"]})
                else:
                    messages.append({"role": "user", "content": message["content"]["text"]})
            st.write(f"Sending conversation to {OpenAiApiModel}...")
            try:
                try:
                    # llmResponseJson = extract_json_object(llmResponse)
                    llmResponseJson = llmJson
                except Exception as e:
                    error = f"Error Parsing {OpenAiApiModel} response in json: {e}"
            except Exception as e:
                error = f"Error Sending conversation **{conversationId}** to {OpenAiApiModel}: {e}"
                
        except Exception as e:
            error = f"Error Fetching conversation **{conversationId}**: {e}"

    analysis.empty()
    
    if error:
        st.error(error, icon='❌')
    else:
        with st.expander(f"🔮 1. {conversationId}"):

            jsonStructure = extract_json_structure(llmResponseJson)

            flatData = flatten_json(llmResponseJson)

            formatedMessages = formalize_messages(messages)
            flatData["conversation"] = formatedMessages

            refJsonFormatPrompt = f"{jsonStructurePrompt}\n\n```json\n{json.dumps(jsonStructure, indent=2)}\n```"

            totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)

            totalInsightCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")
            totalColumnCol.write(f"➡️ Columns :blue-background[**{len(flatData)}**]")
            totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
            TotalMessageCol.write(f"💬 Messages :blue-background[**{len(conversationMessages['history'])}**]")

            formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}

            dataConversation = {}
            dataConversation[conversationId] = formatedFlatData
            
            analysisResults[conversationId] = formatedFlatData

            dfConversations = pd.DataFrame(dataConversation).T

            st.write(dfConversations)

            st.divider()
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    st.chat_message("assistant").write(message["content"]["text"])
                else:
                    st.chat_message("user").write(message["content"]["text"])


            

    st.toast("Analysis Completed", icon="✅")

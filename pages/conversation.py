import pandas as pd
import streamlit as st
import datetime
from src.routes import getAllUsers
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm
from src.utils import getBoxes, getMetrics, getProgress, extract_json_object, flatten_json
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts, getContext
import openai
from src.components.sidebar import sidebar
import json
from src.language import language

# 5a16bb08-8c87-4145-aaf5-2f75c7beb6f4

sidebar("Genii • Conversation Analysis | Conversation",'🧞 :violet[Genii] • Conversation Analysis',"💬 Conversation Analysis")

try:
    allUsers = getAllUsers()
    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]   
except Exception as e:
    st.error(f"**Error Fetching all users** _(try to refresh the app)_", icon='❌')
    st.stop()

projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

conversationId = st.text_input("Enter the conversation ID:")


prompt = st.text_area(
        label="Enter a prompt to analyze the conversations:",
        value=prompts[6],
        height=300,
    )

modelCol, languageCol, analyzeCol = st.columns(3)

with modelCol:
    OpenAiApiModel = st.selectbox(
        "Select a model:",
        ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
        index=2,
        label_visibility="collapsed",
    )

with languageCol:

    resultLanguage = st.selectbox(
        "Select a language:",
        [language for language in language.keys()],
        index=0,
        format_func=lambda x: f"{language[x]} {x}",
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
    allResults = {}
    with analysis.status(f"🔎 1. {conversationId}", expanded=True) as status:
        st.write("analyzing conversation...")
        try:
            conversationMessages = getConversationById(projectId, conversationId)

            prompt = f"{getContext(resultLanguage)}\n{prompt}"
            messages=[{"role": "system", "content": prompt}]
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    messages.append({"role": "assistant", "content": message["content"]["text"]})
                else:
                    messages.append({"role": "user", "content": message["content"]["text"]})
            st.write(f"Sending conversation to {OpenAiApiModel}...")
            try:
                llmResponse = sendMessageToLlm(messages, OpenAiApiModel, client)
                try:
                    llmResponseJson = extract_json_object(llmResponse)
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


            totalInsightCol, TotalMessageCol= st.columns(2)

            totalInsightCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")
            TotalMessageCol.write(f"📦 Messages :blue-background[**{len(conversationMessages['history'])}**]")

            # Aplatir le JSON
            flat_data = flatten_json(llmResponseJson)

            # add projectId as row and flat data as column
            data = {}
            data[projectId] = flat_data
            
            # Convertir en DataFrame
            df = pd.DataFrame(data).T

            st.write(df)

            st.divider()
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    st.chat_message("assistant").write(message["content"]["text"])
                else:
                    st.chat_message("user").write(message["content"]["text"])

    # allResults["conversation Analysis"] = llmResponseJson
    
    # convert all values of keys to string to avoid error
    # llmResponseJson = json.loads(llmResponseJson)
    # data = {key: json.dumps(value, indent=4) if isinstance(value, dict) or isinstance(value, list) else str(value) for key, value in llmResponseJson.items()}
    # df = pd.DataFrame(data, index=[0])
    # st.write(df)

    # st.toast("Analysis Completed", icon="✅")

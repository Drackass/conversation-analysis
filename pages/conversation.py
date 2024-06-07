import pandas as pd
import streamlit as st
import datetime
from src.routes import getAllUsers
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm
from src.utils import getBoxes, getMetrics, getProgress, extract_json_object, flatten_json, extract_json_structure
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts, context, ReportPrompt
import openai
from src.components.sidebar import sidebar
import json
from src.language import language

from src.misc import llmJson

# 5a16bb08-8c87-4145-aaf5-2f75c7beb6f4

sidebar("Genii • Conversation Analysis | Conversation",'🧞 :violet[Genii] • Conversation Analysis',"💬 Conversation Analysis")

try:
    allUsers = getAllUsers()
    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]   
except Exception as e:
    st.error(f"**Error Fetching all users** _(try to refresh the app)_", icon='❌')
    st.stop()

projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

conversationId = st.text_input("Enter the conversation ID:", "5a16bb08-8c87-4145-aaf5-2f75c7beb6f4")

prompt = st.text_area(
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
    allResults = {}
    with analysis.status(f"🔎 1. {conversationId}", expanded=True) as status:
        st.write("analyzing conversation...")
        try:
            conversationMessages = getConversationById(projectId, conversationId)

            prompt = f"{context}\n{prompt}"
            messages=[{"role": "system", "content": prompt}]
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    messages.append({"role": "assistant", "content": message["content"]["text"]})
                else:
                    messages.append({"role": "user", "content": message["content"]["text"]})
            st.write(f"Sending conversation to {OpenAiApiModel}...")
            try:
                # llmResponse = sendMessageToLlm(messages, OpenAiApiModel, client)
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

            # Aplatir le JSON
            flat_data = flatten_json(llmResponseJson)


            totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)

            totalInsightCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")
            totalColumnCol.write(f"➡️ Columns :blue-background[**{len(flat_data)}**]")
            totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
            TotalMessageCol.write(f"💬 Messages :blue-background[**{len(conversationMessages['history'])}**]")



            # Remplacer les "_" par des espaces dans les clés
            flat_data = {key.replace("_", " ").replace("-", " > "): value for key, value in flat_data.items()}

            # add projectId as row and flat data as column
            data = {}
            data[projectId] = flat_data

            # Convertir en DataFrame
            df = pd.DataFrame(data).T

            st.write(df)

            # get a report with llm
            # try:
            #     messages=[]
            #     prompt = f"{ReportPrompt}\n{json.dumps(llmResponseJson, indent=4)}"
            #     messages=[{"role": "system", "content": prompt}]
            #     for message in conversationMessages["history"]:
            #         if message["sender"] == projectId:
            #             messages.append({"role": "assistant", "content": message["content"]["text"]})
            #         else:
            #             messages.append({"role": "user", "content": message["content"]["text"]})

            #     with st.spinner("🧠 Generating report..."):
            #         try:
            #             llmResponse = sendMessageToLlm(messages, OpenAiApiModel, client)
            #         except Exception as e:
            #             st.error(f"Error Sending conversation to {OpenAiApiModel}: {e}", icon='❌')
            #             st.stop()
            #     st.markdown(llmResponse)

            # except Exception as e:
            #     st.error(f"Error Sending conversation to {OpenAiApiModel}: {e}", icon='❌')

            st.divider()
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    st.chat_message("assistant").write(message["content"]["text"])
                else:
                    st.chat_message("user").write(message["content"]["text"])

            extractedJsonStructure = extract_json_structure(llmResponseJson)
            st.write(extractedJsonStructure)

    st.toast("Analysis Completed", icon="✅")

import streamlit as st
import datetime
from src.routes import getAllUsers
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm, sendCompletionToLlm
from src.utils import flatten_json, extract_json_structure, formalize_messages, extract_json_object
from src.prompts import prompts, context, jsonStructurePrompt, reportPrompt
import openai
import pandas as pd
from src.components.sidebar import sidebar
from src.misc import llmJson, dummyReport
import json

sidebar("Genii • Conversation Analysis | Project Conversations", '🧞 :violet[Genii] • Conversation Analysis', "🔮 Project Conversations Analysis")

try:
    allUsers = getAllUsers()
    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]   
except Exception as e:
    st.error(f"**Error Fetching all users** _(try to refresh the app)_", icon='❌')
    st.stop()

projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

filters = st.multiselect(
"Filters",
["Conversation Limit", "Date Range"],
["Conversation Limit"],
)

params = {}
conversationLimit = None
if "Conversation Limit" in filters:
    with st.container(border=True):
            conversationLimit = st.select_slider(
            "Select a conversations limit",
            options= range(1, 21),
            value=5,
        ),
    params['limit'] = conversationLimit[0]
conversationDateRange = None
if "Date Range" in filters:
    with st.container(border=True):
        conversationDateRange = st.date_input("Select a range", (datetime.datetime.now() - datetime.timedelta(days=10), datetime.datetime.now()))
    params['range'] = '{"conditions":[{"operator":"gte","value":"' + conversationDateRange[0].isoformat() + '"},{"operator":"lte","value":"' + conversationDateRange[1].isoformat() + '"}],"field":"date"}'
    params['sort'] = '[{"field":"date","sort":"desc"}]'
    params['offset'] = 0
else:
    params['range'] = '{{"conditions":[{{"operator":"gte","value":"{}"}},{{"operator":"lte","value":"{}"}}],"field":"date"}}'.format((datetime.datetime.now() - datetime.timedelta(days=3650)).isoformat(), datetime.datetime.now().isoformat())
    params['sort'] = '[{"field":"date","sort":"desc"}]'
    params['offset'] = 0

with st.expander('🔎 Analysis Prompts'):
    customPrompt = st.text_area(
            label="Enter a prompt to analyze the conversations:",
            value=prompts[6],
            height=300,
        )
    OpenAiApiModel = st.selectbox(
        "Select a model:",
        ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
        index=3,
        label_visibility="collapsed",
        key="OpenAiApiModel",
    )
    

with st.expander('📖 Report Prompts'):
    customPromptReport = st.text_area(
            label="Enter a prompt to generate a conversations report:",
            value=reportPrompt,
            height=300,
            key="customPromptReport",
        )
    
    OpenAiApiModelReport = st.selectbox(
        "Select a model:",
        ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
        index=3,
        label_visibility="collapsed",
    )

# modelCol, analyzeCol = st.columns(2)

# with modelCol:
    # OpenAiApiModel = st.selectbox(
    #     "Select a model:",
    #     ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
    #     index=3,
    #     label_visibility="collapsed",
    # )

# with analyzeCol:
#     btnAnalyze= st.button(
#         "Analyze",
#         use_container_width=True,
#         type="primary",
#         )

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

    conversationsAnalysis = []
    with st.spinner(f'Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
        try:
            conversations = getConversationsByProjectId(projectId, params)
            st.success(f'Fetched {len(conversations["data"]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}** successfully', icon='✅')
        except Exception as e:
            st.error(f"❌ Error Fetching {conversationLimit[0] if ('Conversation Limit' in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ('Date Range' in filters) else ''} for project **{projectId}**: {e}")
            st.stop()
    

    indexConversation = 1
    analysisResultsFormated = {}
    analysisResults= {}
    refJsonFormatPrompt = ""
    for conversation in conversations["data"]:
        
        conversationId = conversation["id"] 
        error = ""
        analysis = st.empty()

        with analysis.status(f"🔎 {indexConversation}. {conversation['summary']} : {conversationId}", expanded=True) as status:
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
                    llmResponse = sendMessageToLlm(messages, OpenAiApiModel, client)
                    try:
                        llmResponseJson = extract_json_object(llmResponse)
                        # llmResponseJson = llmJson
                    except Exception as e:
                        error = f"Error Parsing {OpenAiApiModel} response in json: {e}"
                except Exception as e:
                    error = f"Error Sending conversation **{conversationId}** to {OpenAiApiModel}: {e}"
                    
            except Exception as e:
                error = f"Error Fetching conversation **{conversationId}**: {e}"

        analysis.empty()
        if error:
            st.error(error, icon='❌')
            indexConversation += 1
        else:
            with st.expander(f"🔮 {indexConversation}. {conversation['summary']} : {conversationId}"):
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


                dfConversations = pd.DataFrame(dataConversation).T

                st.write(dfConversations)

                st.divider()
                for message in conversationMessages["history"]:
                    if message["sender"] == projectId:
                        st.chat_message("assistant").write(message["content"]["text"])
                    else:
                        st.chat_message("user").write(message["content"]["text"])
                        
                indexConversation += 1

        analysisResultsFormated[conversationId] = formatedFlatData
        analysisResults[conversationId] = llmResponseJson


    with st.expander(f'🧠 Report of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
        totalColumnCol, totalProjectRow= st.columns(2)

        totalColumnCol.write(f"➡️ Columns :blue-background[**{len(flatData)}**]")
        totalProjectRow.write(f"⬇️ Row :blue-background[**{len(conversations['data'])}**]")

        formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}
        df = pd.DataFrame(analysisResultsFormated).T
        st.write(df)

        st.divider()

        with st.spinner("🧠 Generating Report..."):
            with st.container(border=True):
                reportPromptWithVerbatim = f"{customPromptReport}\n\n```json\n{json.dumps(analysisResults, indent=2)}\n```"
                report = sendCompletionToLlm(reportPromptWithVerbatim, OpenAiApiModelReport, client)
                # report = dummyReport
                with st.popover("Copy"):
                    st.code(report, language="markdown")
                st.markdown(report)



               
    st.toast("Analysis Completed", icon="✅")
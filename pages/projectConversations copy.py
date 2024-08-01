# import asyncio
# import datetime
# from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm, sendCompletionToLlm, generateReport
# from src.shared.utils import flatten_json, extract_json_structure, formalize_messages, extract_json_object
# from src.shared.prompts import prompts, context, jsonStructurePrompt, reportPrompt, refJsonStructurePrompt
# import openai
# import pandas as pd
# import json
# from openai import AsyncOpenAI
# import asyncio

# import streamlit as st
# from src.components.sidebar import Sidebar
# from src.shared.geniiUtlis import getAllUsers

# Sidebar("Genii • Conversation Analysis | Project Conversations", '🧞 :violet[Genii] • Conversation Analysis', "🔮 Project Conversations Analysis")

# try:
#     allUsers = getAllUsers()
#     allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]   
# except Exception as e:
#     st.error(f"**Error Fetching all users** _(try to refresh the app)_", icon='❌')
#     st.stop()

# projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

# filters = st.multiselect(
# "Filters",
# ["Conversation Limit", "Date Range"],
# ["Conversation Limit"],
# )

# params = {}
# conversationLimit = None
# if "Conversation Limit" in filters:
#     with st.container(border=True):
#             conversationLimit = st.select_slider(
#             "Select a conversations limit",
#             options= range(1, 201),
#             value=5,
#         ),
#     params['limit'] = conversationLimit[0]
# conversationDateRange = None
# if "Date Range" in filters:
#     with st.container(border=True):
#         conversationDateRange = st.date_input("Select a range", (datetime.datetime.now() - datetime.timedelta(days=10), datetime.datetime.now()))
#     params['range'] = '{"conditions":[{"operator":"gte","value":"' + conversationDateRange[0].isoformat() + '"},{"operator":"lte","value":"' + conversationDateRange[1].isoformat() + '"}],"field":"date"}'
#     params['sort'] = '[{"field":"date","sort":"desc"}]'
#     params['offset'] = 0
# else:
#     params['range'] = '{{"conditions":[{{"operator":"gte","value":"{}"}},{{"operator":"lte","value":"{}"}}],"field":"date"}}'.format((datetime.datetime.now() - datetime.timedelta(days=3650)).isoformat(), datetime.datetime.now().isoformat())
#     params['sort'] = '[{"field":"date","sort":"desc"}]'
#     params['offset'] = 0

# with st.expander('🔎 Analysis Prompts'):
#     customPrompt = st.text_area(
#             label="Enter a prompt to analyze the conversations:",
#             value=prompts[6],
#             height=300,
#         )
#     OpenAiApiModel = st.selectbox(
#         "Select a model:",
#         ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
#         index=3,
#         label_visibility="collapsed",
#         key="OpenAiApiModel",
#     )

# with st.expander('📖 Report Prompts'):
#     customPromptReport = st.text_area(
#             label="Enter a prompt to generate a conversations report:",
#             value=reportPrompt,
#             height=300,
#             key="customPromptReport",
#         )
    
#     OpenAiApiModelReport = st.selectbox(
#         "Select a model:",
#         ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5"],
#         index=3,
#         label_visibility="collapsed",
#     )

# # with st.expander('⚙️ Advanced Settings'):
# #     toggleShowConversations = st.toggle("Show Conversations", True)
# #     toogleReportByConversation = st.toggle("Report by Conversation", False)

# btnAnalyze= st.button(
#     "Analyze",
#     use_container_width=True,
#     type="primary",
#     )

# client_asynchrone = AsyncOpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# client_synchrone = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
# if btnAnalyze:

#     # st.divider()

#     # analysisStatus = st.empty()

#     # with analysisStatus.status(f"🔍 Analysis of {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversations {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}**", expanded=True):
#     #     st.write(f"📦 Sending a request to {OpenAiApiModel} to get the json structure of the analysis...")
#     #     time.sleep(3)
#     #     st.write(f"💬 Fetching {conversationLimit[0] if ('Conversation Limit' in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ('Date Range' in filters) else ''} for project **{projectId}**")
#     #     time.sleep(3)
#     #     st.write(f"🔎 Sending each conversation to {OpenAiApiModel} for analysis...")
#     #     time.sleep(3)
#     #     # my_bar = st.progress(20,text="")
#     #     # for percent_complete in range(100):
#     #     #     time.sleep(0.1)
#     #     #     my_bar.progress(percent_complete + 1, text=f"Analyzing {percent_complete + 1}%")

#     #     my_bar = st.progress(0)
#     #     for conversationAnalysed in range(conversationLimit[0]):
#     #         time.sleep(1)
#     #         my_bar.progress(math.ceil(((conversationAnalysed + 1) * 100)/conversationLimit[0]), text=f"🔮 {conversationAnalysed + 1}/{conversationLimit[0]} Conversations Analysed")
        
#     # analysisStatus.empty()

#     # with st.expander(f'📚 Report of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#     #     st.write(dummyReport)

#     # with st.expander(f'🔮 Analysis of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#     #     st.write(llmJson)
#     # with st.expander(f'🔮 Analysis of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#     #     st.write(llmJson)
#     # with st.expander(f'🔮 Analysis of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#     #     st.write(llmJson)

#     st.divider()

#     refJsonFormat = ""
#     with st.spinner(f"Sending a request to {OpenAiApiModel} to get the structure of the analysis..."):
#         try:
#             llmResponse= sendCompletionToLlm(f"{refJsonStructurePrompt}\n{customPrompt}", OpenAiApiModel, client_synchrone)

#             try:
#                 extractedJsonStructure = extract_json_object(llmResponse)
#                 refJsonStructure = extract_json_structure(extractedJsonStructure)
#                 st.success(f"Received the structure of the analysis from {OpenAiApiModel} successfully", icon='✅')
#             except Exception as e:
#                 st.error(f"❌ Error Parsing {OpenAiApiModel} response in json: {e}")
#                 st.stop()
#         except Exception as e:
#             st.error(f"❌ Error Sending a request to {OpenAiApiModel} to get the structure of the analysis: {e}")
#             st.stop()

#     conversationsAnalysis = []
#     with st.spinner(f'Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#         try:
#             conversations = getConversationsByProjectId(projectId, params)
#             st.success(f'Fetched {len(conversations["data"]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}** successfully', icon='✅')
#         except Exception as e:
#             st.error(f"❌ Error Fetching {conversationLimit[0] if ('Conversation Limit' in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ('Date Range' in filters) else ''} for project **{projectId}**: {e}")
#             st.stop()
    
#     async def conversationAnalysis(conversation):
#         conversationId = conversation["id"] 
#         error = ""
#         analysis = st.empty()

#         with analysis.status(f"🔎 {conversation['summary']} : {conversationId}", expanded=False):
#             st.write("analyzing conversation...")

#             try:
#                 conversationMessages = await getConversationById(projectId, conversationId)

#                 analysisPrompt = f"{context}\n{customPrompt}\n\n{jsonStructurePrompt}\n\n```json\n{json.dumps(refJsonStructure, indent=2)}\n```"
#                 messages=[{"role": "system", "content": analysisPrompt}]
#                 for message in conversationMessages["history"]:
#                     if message["sender"] == projectId:
#                         messages.append({"role": "assistant", "content": message["content"]["text"]})
#                     else:
#                         messages.append({"role": "user", "content": message["content"]["text"]})

#                 st.write(f"Sending conversation to {OpenAiApiModel}...")
#                 try:
#                     llmResponse = await sendMessageToLlm(messages, OpenAiApiModel, client_asynchrone)
#                     try:
#                         llmResponseJson = extract_json_object(llmResponse)
#                         # llmResponseJson = llmJson
#                     except Exception as e:
#                         error = f"Error Parsing {OpenAiApiModel} response in json: {e}"

#                 except Exception as e:
#                     error = f"Error Sending conversation **{conversationId}** to {OpenAiApiModel}: {e}"
            
#             except Exception as e:
#                 error = f"Error Fetching conversation **{conversationId}**: {e}"

#         analysis.empty()
#         if error:
#             st.error(error, icon='❌')
#         else:
#             with st.expander(f"🔮 {conversation['summary']} : {conversationId}"):
#                 flatData = flatten_json(llmResponseJson)

#                 formatedMessages = formalize_messages(messages)
#                 flatData["conversation"] = formatedMessages

#                 totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)

#                 totalInsightCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")
#                 totalColumnCol.write(f"➡️ Columns :blue-background[**{len(flatData)}**]")
#                 totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
#                 TotalMessageCol.write(f"💬 Messages :blue-background[**{len(conversationMessages['history'])}**]")

#                 formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}

#                 dataConversation = {}
#                 dataConversation[conversationId] = formatedFlatData

#                 dfConversations = pd.DataFrame(dataConversation).T

#                 st.write(dfConversations)

#                 st.divider()
#                 for message in conversationMessages["history"]:
#                     if message["sender"] == projectId:
#                         st.chat_message("assistant").write(message["content"]["text"])
#                     else:
#                         st.chat_message("user").write(message["content"]["text"])

#         analysisResultsFormated[conversationId] = formatedFlatData
#         analysisResults[conversationId] = llmResponseJson

#     analysisResultsFormated = {}
#     analysisResults = {}
#     flatData = {}
#     async def conversationsAnalysisTasks():
#         global analysisResultsFormated, analysisResults, flatData, refJsonStructure
#         tasks = []
#         for conversation in conversations["data"]:
#             task = conversationAnalysis(conversation)
#             tasks.append(task)
#         await asyncio.gather(*tasks)

#     asyncio.run(conversationsAnalysisTasks())

#     with st.expander(f'📚 Report of {"the " + str(conversationLimit[0]) if ("Conversation Limit" in filters) else "all"} conversions {f"between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**" if ("Date Range" in filters) else ""} for project **{projectId}**'):
#         formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}
#         df = pd.DataFrame(analysisResultsFormated).T
#         st.write(df)

#         st.divider()

#         reportPromptWithVerbatim = f"{customPromptReport}\n\n```json\n{json.dumps(analysisResults, indent=2)}\n```"
#         reportContainer = st.container(border=True).empty()

#         generateReport(reportPromptWithVerbatim, OpenAiApiModelReport, client_synchrone, reportContainer)

#     st.toast("Analysis Completed", icon="✅")
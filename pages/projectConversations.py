import csv
import numpy as np
import streamlit as st
import datetime
from src.routes import getAllUsers
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm
from src.utils import getBoxes, getMetrics, getProgress, extract_json_object
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts
import openai
import pandas as pd

st.set_page_config(
    page_title="Genii • Conversation Analysis | Project Conversations",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.page_link("__main__.py", label="Introduction", icon="🧞")
    st.page_link("pages/projectConversations.py", label="Project Conversations", icon="🔮")
    st.page_link("pages/conversation.py", label="Conversation", icon="💬")
    st.page_link("pages/datasetFile.py", label="Dataset File", icon="📄")
    st.page_link("pages/customDataset.py", label="Custom Dataset", icon="📝")
    st.page_link("pages/help.py", label="Help Center", icon="🛟")

TOLKAI_LOGO = "genii.svg"
st.logo(TOLKAI_LOGO)

st.title('🧞 :violet[Genii] • Conversation Analysis')
st.header("🔮 Project Conversations Analysis")

allUsers = getAllUsers()
allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]

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








prompt = st.text_area(
        label="Enter a prompt to analyze the conversations:",
        value=prompts[5],
        height=300,
    )

modelCol, analyzeCol = st.columns(2)

with modelCol:
    azureOpenAiApiModel = st.selectbox(
        "Select a model:",
        [model for model in azureOpenAiApiCredentials.keys()],
        index=2,
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

    deployment_name = azureOpenAiApiCredentials[azureOpenAiApiModel]["deployment_name"]
    azure_endpoint = azureOpenAiApiCredentials[azureOpenAiApiModel]["azure_endpoint"]
    api_key = azureOpenAiApiCredentials[azureOpenAiApiModel]["api_key"]
    api_version = azureOpenAiApiCredentials[azureOpenAiApiModel]["api_version"]

    client = openai.AzureOpenAI(
        azure_endpoint = azure_endpoint, 
        api_key=api_key,  
        api_version=api_version
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
    allResults = {}
    for conversation in conversations["data"]:
        
        conversationId = conversation["id"] 
        error = ""
        analysis = st.empty()
        with analysis.status(f"🔎 {indexConversation}. {conversation['summary']} : {conversationId}", expanded=True) as status:
            st.write("analyzing conversation...")
            try:
                conversationMessages = getConversationById(projectId, conversationId)
                messages=[{"role": "system", "content": prompt}]
                for message in conversationMessages["history"]:
                    if message["sender"] == projectId:
                        messages.append({"role": "assistant", "content": message["content"]["text"]})
                    else:
                        messages.append({"role": "user", "content": message["content"]["text"]})
                st.write(f"Sending conversation to {azureOpenAiApiModel}...")
                try:
                    llmResponse = sendMessageToLlm(messages, deployment_name, client)
                    try:
                        llmResponseJson = extract_json_object(llmResponse)
                    except Exception as e:
                        error = f"Error Parsing {azureOpenAiApiModel} response in json: {e}"


                except Exception as e:
                    error = f"Error Sending conversation **{conversationId}** to {azureOpenAiApiModel}: {e}"
                    
            except Exception as e:
                error = f"Error Fetching conversation **{conversationId}**: {e}"

        analysis.empty()
        if error:
            st.error(error, icon='❌')
            indexConversation += 1
        else:
            with st.expander(f"🔮 {indexConversation}. {conversation['summary']} : {conversationId}"):
                totalCol, boxesCol, metricsCol, progressCol = st.columns(4)
                totalCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")

                boxes = getBoxes(llmResponseJson)
                boxesCol.write(f"📦 Boxes :blue-background[**{len(boxes)}**]")
                for key, value in boxes.items():
                    if value["type"] == "success":
                        st.success(f" **{value['label']}**: {value['value']}", icon=value["icon"])
                    elif value["type"] == "warning":
                        st.warning(f" **{value['label']}**: {value['value']}", icon=value["icon"])
                    elif value["type"] == "error":
                        st.error(f" **{value['label']}**: {value['value']}", icon=value["icon"])
                    else:
                        st.info(f" **{value['label']}**: {value['value']}", icon=value["icon"])
                        

                metrics = getMetrics(llmResponseJson)
                metricsCol.write(f"📊 Metrics :blue-background[**{len(metrics)}**]")
                num_metrics = len(metrics)
                num_columns = 4
                num_rows = num_metrics // num_columns + (num_metrics % num_columns > 0)
                metric_index = 0
                for row in range(num_rows):
                    cols = st.columns(num_columns)
                    for col in cols:
                        if metric_index < num_metrics:
                            metric = metrics[list(metrics.keys())[metric_index]]
                            col.container(border=True).metric(metric["name"], metric["value"], f"{metric['delta']}%")
                            metric_index += 1

                progress = getProgress(llmResponseJson)
                progressCol.write(f"📈 Progress :blue-background[**{len(progress)}**]")
                num_progress = len(progress)
                num_columns = 4
                num_rows = num_progress // num_columns + (num_progress % num_columns > 0)
                progress_index = 0
                for row in range(num_rows):
                    cols = st.columns(num_columns)
                    for col in cols:
                        if progress_index < num_progress:
                            progress_value = progress[list(progress.keys())[progress_index]]
                            col.container(border=True).progress(progress_value["value"] if progress_value["value"] is not None else 0, progress_value["name"])
                            progress_index += 1

                # convert llmResponseJson to a csv file with insights as columns and conversationsId as rows
                


                st.divider()
                for message in conversationMessages["history"]:
                    if message["sender"] == projectId:
                        st.chat_message("assistant").write(message["content"]["text"])
                    else:
                        st.chat_message("user").write(message["content"]["text"])
                indexConversation += 1

        # llmResponseJson["conversation"] = messages
        # st.json(llmResponseJson)
        allResults[conversationId] = llmResponseJson

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.T.to_csv().encode("utf-8")  # Transpose the dataframe

    # convert allResults to a csv file with insights as rows and conversationsId as columns
    df = pd.DataFrame(allResults).T  # Transpose the dataframe
    # df = pd.DataFrame(allResults).T.astype(str)  # Transpose the dataframe and convert all values to string
    st.write(df)


    csv = convert_df(df)

    st.download_button(
        label="📥 Download Insights",
        data=csv,
        file_name="insights.csv",
        mime="text/csv",
    )

    st.toast("Analysis Completed", icon="✅")
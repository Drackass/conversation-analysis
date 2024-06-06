import pandas as pd
import streamlit as st
import datetime
from src.routes import getAllUsers
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm
from src.utils import getBoxes, getMetrics, getProgress, extract_json_object
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts
import openai
from src.components.sidebar import sidebar
import json

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
        value=prompts[7],
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

    error = ""
    analysis = st.empty()
    allResults = {}
    with analysis.status(f"🔎 1. {conversationId}", expanded=True) as status:
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
                llmResponseJson = llmResponse
                # try:
                #     llmResponseJson = extract_json_object(llmResponse)
                # except Exception as e:
                #     error = f"Error Parsing {azureOpenAiApiModel} response in json: {e}"
            except Exception as e:
                error = f"Error Sending conversation **{conversationId}** to {azureOpenAiApiModel}: {e}"
                
        except Exception as e:
            error = f"Error Fetching conversation **{conversationId}**: {e}"

    analysis.empty()
    if error:
        st.error(error, icon='❌')
    else:
        with st.expander(f"🔮 1. {conversationId}"):
            # st.write(llmResponseJson)
            st.json(llmResponseJson)


            # totalCol, boxesCol, metricsCol, progressCol = st.columns(4)
            # totalCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")

            # boxes = getBoxes(llmResponseJson)
            # boxesCol.write(f"📦 Boxes :blue-background[**{len(boxes)}**]")
            # for key, value in boxes.items():
            #     if value["type"] == "success":
            #         st.success(f" **{value['label']}**: {value['value']}", icon=value["icon"])
            #     elif value["type"] == "warning":
            #         st.warning(f" **{value['label']}**: {value['value']}", icon=value["icon"])
            #     elif value["type"] == "error":
            #         st.error(f" **{value['label']}**: {value['value']}", icon=value["icon"])
            #     else:
            #         st.info(f" **{value['label']}**: {value['value']}", icon=value["icon"])
                    

            # metrics = getMetrics(llmResponseJson)
            # metricsCol.write(f"📊 Metrics :blue-background[**{len(metrics)}**]")
            # num_metrics = len(metrics)
            # num_columns = 4
            # num_rows = num_metrics // num_columns + (num_metrics % num_columns > 0)
            # metric_index = 0
            # for row in range(num_rows):
            #     cols = st.columns(num_columns)
            #     for col in cols:
            #         if metric_index < num_metrics:
            #             metric = metrics[list(metrics.keys())[metric_index]]
            #             col.container(border=True).metric(metric["name"], metric["value"], f"{metric['delta']}%")
            #             metric_index += 1

            # progress = getProgress(llmResponseJson)
            # progressCol.write(f"📈 Progress :blue-background[**{len(progress)}**]")
            # num_progress = len(progress)
            # num_columns = 4
            # num_rows = num_progress // num_columns + (num_progress % num_columns > 0)
            # progress_index = 0
            # for row in range(num_rows):
            #     cols = st.columns(num_columns)
            #     for col in cols:
            #         if progress_index < num_progress:
            #             progress_value = progress[list(progress.keys())[progress_index]]
            #             col.container(border=True).progress(progress_value["value"] if progress_value["value"] is not None else 0, progress_value["name"])
            #             progress_index += 1
            st.divider()
            for message in conversationMessages["history"]:
                if message["sender"] == projectId:
                    st.chat_message("assistant").write(message["content"]["text"])
                else:
                    st.chat_message("user").write(message["content"]["text"])

    # allResults["conversation Analysis"] = llmResponseJson
    
    # convert all values of keys to string to avoid error
    llmResponseJson = json.loads(llmResponseJson)
    data = {key: json.dumps(value, indent=4) if isinstance(value, dict) or isinstance(value, list) else str(value) for key, value in llmResponseJson.items()}
    df = pd.DataFrame(data, index=[0])
    st.write(df)

    st.toast("Analysis Completed", icon="✅")

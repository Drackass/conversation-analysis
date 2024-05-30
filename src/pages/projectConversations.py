import streamlit as st
import datetime
from src.prompts import prompts
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.routes import getConversationById, getConversationsByProjectId, sendMessageToLlm
from src.utils import extract_json_object, getBoxes, getMetrics, getProgress
from src.config import azureOpenAiApiModel, projectId, conversationLimit, conversationDateRange
import openai

def projectConversationsPage():
    st.header("Project Conversations Analysis")

    projectId = st.text_input("Enter a projectId:", "e51255e3-2790-4ab7-964c-6f898f7e00f7")

    filters = st.multiselect(
    "Filters",
    ["Conversation Limit", "Date Range"],
    ["Conversation Limit", "Date Range"],
    )

    if "Conversation Limit" in filters:
        with st.container(border=True):
                conversationLimit = st.select_slider(
                "Select a conversations limit",
                options= range(1, 21),
                value=5,
            ),

    if "Date Range" in filters:
        with st.container(border=True):
            conversationDateRange = st.date_input("Select a range", (datetime.datetime.now() - datetime.timedelta(days=10), datetime.datetime.now()))

    prompt = st.text_area(
        label="Enter a prompt to analyze the conversations:",
        value=prompts[5],
        height=200,
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
        try:
            with st.spinner(f'Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}**'):
                try:
                    params = {}
                    if "Conversation Limit" in filters:
                        params['limit'] = conversationLimit[0]
                    if "Date Range" in filters:
                        params['range'] = '{"conditions":[{"operator":"gte","value":"' + conversationDateRange[0].isoformat() + '"},{"operator":"lte","value":"' + conversationDateRange[1].isoformat() + '"}],"field":"date"}'
                        params['sort'] = '[{"field":"date","sort":"desc"}]'
                        params['offset'] = 0
                    else:
                        params['range'] = '{{"conditions":[{{"operator":"gte","value":"{}"}},{{"operator":"lte","value":"{}"}}],"field":"date"}}'.format((datetime.datetime.now() - datetime.timedelta(days=3650)).isoformat(), datetime.datetime.now().isoformat())
                        params['sort'] = '[{"field":"date","sort":"desc"}]'
                        params['offset'] = 0
                    conversations = getConversationsByProjectId(projectId, params)
                    st.success(f'Fetched {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}** successfully', icon='✅')

                except Exception as e:
                    st.error(f"❌ Error Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}**: {e}")
                    st.stop()

            indexConversation = 1
            deployment_name = azureOpenAiApiCredentials[azureOpenAiApiModel]["deployment_name"]
            azure_endpoint = azureOpenAiApiCredentials[azureOpenAiApiModel]["azure_endpoint"]
            api_key = azureOpenAiApiCredentials[azureOpenAiApiModel]["api_key"]
            api_version = azureOpenAiApiCredentials[azureOpenAiApiModel]["api_version"]

            client = openai.AzureOpenAI(
                azure_endpoint = azure_endpoint, 
                api_key=api_key,  
                api_version=api_version
            )
            try:
                for conversation in conversations["data"]:
                    conversationId = conversation["id"] 
                    with st.empty():
                        with st.status(f"🔎 {indexConversation}. {conversation["summary"]} : {conversationId}", expanded=True) as status:
                            st.write("analyzing conversation...")
                            try:
                                conversationMessages = getConversationById(projectId, conversationId)
                            except Exception as e:
                                st.error(f"❌ Error analyzing conversation {conversationId}: {e}")
                                st.stop()

                            messages=[{"role": "system", "content": prompt}]
                            for message in conversationMessages["history"]:
                                if message["sender"] == projectId:
                                    messages.append({"role": "assistant", "content": message["content"]["text"]})
                                else:
                                    messages.append({"role": "user", "content": message["content"]["text"]})
                            st.write(f"Sending conversation to {azureOpenAiApiModel}...")
                            try:
                                llmResponse = sendMessageToLlm(messages, deployment_name, client)
                            except Exception as e:
                                st.error(f"❌ Error sending conversation to {azureOpenAiApiModel}: {e}")
                                st.stop()
                            status.update(label="Analyse complete!", state="complete", expanded=False)
                        st.empty()

                    with st.expander(f"🔮 {indexConversation}. {conversation["summary"]} : {conversationId}"):
                        llmResponseJson = extract_json_object(llmResponse)

                        totalCol, boxesCol, metricsCol, progressCol = st.columns(4)

                        # number of insights
                        totalCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")

                        # get the boxes from llmResponseJson
                        boxes = getBoxes(llmResponseJson)
                        boxesCol.write(f"📦 Boxes :blue-background[**{len(boxes)}**]")
                        for key, value in boxes.items():
                            # st.write(f"🔍 **{key}**: {value}")
                            if value["type"]:
                                st.info(f" **{value["label"]}**: {value["value"]}", icon=value["icon"])

                        # get the metrics from llmResponseJson
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
                                    # col.metric(metric["name"], metric["value"], f"{metric['delta']}%")
                                    metric_index += 1

                        # get the progress from llmResponseJson
                        progress = getProgress(llmResponseJson)
                        progressCol.write(f"📈 Progress :blue-background[**{len(progress)}**]")
                        # for key, value in progress.items():
                        #     # st.write(f"🔍 **{value['name']}**: {value['value']}")
                        #     st.progress(value["value"], value["name"])

                        num_progress = len(progress)
                        num_columns = 4
                        num_rows = num_progress // num_columns + (num_progress % num_columns > 0)
                        progress_index = 0
                        for row in range(num_rows):
                            cols = st.columns(num_columns)
                            for col in cols:
                                if progress_index < num_progress:
                                    progress_value = progress[list(progress.keys())[progress_index]]
                                    col.container(border=True).progress(progress_value["value"], progress_value["name"])
                                    # col.progress(progress_value["value"], progress_value["name"])
                                    progress_index += 1



                        st.divider()
                        for message in conversationMessages["history"]:
                            if message["sender"] == projectId:
                                st.chat_message("assistant").write(message["content"]["text"])
                            else:
                                st.chat_message("user").write(message["content"]["text"])

                    indexConversation += 1
            except KeyError:
                st.error("❌ Error: Invalid projectId")
                st.stop()

        except KeyError:
            st.error("Invalid promptId")
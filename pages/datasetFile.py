import streamlit as st
import pandas as pd
from io import StringIO
from src.routes import getConversationById, sendMessageToLlm
from src.utils import getBoxes, getMetrics, getProgress, extract_json_object
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts
import openai
from src.components.sidebar import sidebar

sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "📄 Dataset File Analysis")

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file)


    

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

    error = ""
    analysis = st.empty()
    allResults = {}
    with analysis.status(f"🔎 Analysis in progress", expanded=True) as status:

        messages = [{"role": "system", "content": prompt}]
        for row in dataframe.iterrows():
            if row[1][0] == 'user':
                messages.append({"role": "user", "content": row[1][1]})
            else:
                messages.append({"role": "assistant", "content": row[1][1]})

        st.write(f"Sending conversation to {azureOpenAiApiModel}...")
        try:
            llmResponse = sendMessageToLlm(messages, deployment_name, client)
            try:
                llmResponseJson = extract_json_object(llmResponse)
            except Exception as e:
                error = f"Error Parsing {azureOpenAiApiModel} response in json: {e}"
        except Exception as e:
            error = f"Error Sending conversation to {azureOpenAiApiModel}: {e}"

    analysis.empty()
    if error:
        st.error(error, icon='❌')
    else:
        with st.expander(f"🔮 Analysis complete"):
            totalCol, boxesCol, metricsCol, progressCol = st.columns(4)
            totalCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")

            boxes = getBoxes(llmResponseJson)
            boxesCol.write(f"📦 Boxes :blue-background[**{len(boxes)}**]")
            for key, value in boxes.items():
                if value["type"] == "success":
                    st.success(f" **{value['label']}**: {value['value']}", icon=value['icon'])
                elif value["type"] == "warning":
                    st.warning(f" **{value['label']}**: {value['value']}", icon=value['icon'])
                elif value["type"] == "error":
                    st.error(f" **{value['label']}**: {value['value']}", icon=value['icon'])
                else:
                    st.info(f" **{value['label']}**: {value['value']}", icon=value['icon'])


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
                st.divider()

                for message in messages:
                    if message["role"] == "assistant":
                        st.chat_message("assistant").write(message["content"])
                    elif message["role"] == "user":
                        st.chat_message("user").write(message["content"])

    allResults["conversation Analysis"] = llmResponseJson

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.T.to_csv().encode("utf-8")  # Transpose the dataframe

    # convert allResults to a csv file with insights as rows and conversationsId as columns
    df = pd.DataFrame(allResults).T  # Transpose the dataframe
    st.write(df)

    csv = convert_df(df)

    st.download_button(
        label="📥 Download Insights",
        data=csv,
        file_name="insights.csv",
        mime="text/csv",
    )   

    st.toast("Analysis Completed", icon="✅")

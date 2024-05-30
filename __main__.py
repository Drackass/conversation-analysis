from io import StringIO
from turtle import pd
import openai
import streamlit as st
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.prompts import prompts
from src.routes import getConversationById, getConversationsByProjectId, sendMessageToLlm
from src.utils import extract_json_object, getBoxes, getMetrics, getProgress
from src.tabs.projectConversations import projectConversationsTab
# from src.tabs.conversation import conversationTab

st.set_page_config(
    page_title="Tolk.ai • Conversation Analysis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "This is a dashboard to analyze conversations from Tolk.ai."
    }
)

st.title('🔮 :violet[Tolk.ai] • Conversation Analysis')

ProjectConversationsTab, ConversationTab, DatasetFileTab = st.tabs(["🤖 Project Conversations", "💬 Conversation", "📄 Dataset File"])

with ProjectConversationsTab:
    projectId, filters, params, conversationLimit, conversationDateRange = projectConversationsTab()
            
with ConversationTab:
    # projectId, conversationId = conversationTab()
    st.header("Conversation Analysis")

with DatasetFileTab:
    st.header("Dataset File Analysis")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        st.write(bytes_data)

        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)
    # info for the structure of the file to be uploaded
    st.info('The file should be a **csv** file with the following structure: _user/agent : message_', icon='📄')

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
    with st.spinner(f'Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}**'):
        try:
            conversations = getConversationsByProjectId(projectId, params)
            st.success(f'Fetched {len(conversations["data"]) if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}** successfully', icon='✅')
        except Exception as e:
            st.error(f"❌ Error Fetching {conversationLimit[0] if ("Conversation Limit" in filters) else 'all'} conversions {f'between **{conversationDateRange[0]}** and **{conversationDateRange[1]}**' if ("Date Range" in filters) else ''} for project **{projectId}**: {e}")
            st.stop()
    

    indexConversation = 1
    for conversation in conversations["data"]:
        
        conversationId = conversation["id"] 
        error = ""
        analysis = st.empty()
        with analysis.status(f"🔎 {indexConversation}. {conversation["summary"]} : {conversationId}", expanded=True) as status:
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
            with st.expander(f"🔮 {indexConversation}. {conversation["summary"]} : {conversationId}"):
                totalCol, boxesCol, metricsCol, progressCol = st.columns(4)
                totalCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")

                boxes = getBoxes(llmResponseJson)
                boxesCol.write(f"📦 Boxes :blue-background[**{len(boxes)}**]")
                for key, value in boxes.items():
                    if value["type"] == "success":
                        st.success(f" **{value["label"]}**: {value["value"]}", icon=value["icon"])
                    elif value["type"] == "warning":
                        st.warning(f" **{value["label"]}**: {value["value"]}", icon=value["icon"])
                    elif value["type"] == "error":
                        st.error(f" **{value["label"]}**: {value["value"]}", icon=value["icon"])
                    else:
                        st.info(f" **{value["label"]}**: {value["value"]}", icon=value["icon"])
                        

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
                    for message in conversationMessages["history"]:
                        if message["sender"] == projectId:
                            st.chat_message("assistant").write(message["content"]["text"])
                        else:
                            st.chat_message("user").write(message["content"]["text"])
                indexConversation += 1
import datetime
from io import StringIO
import time
from turtle import pd
import numpy as np
import openai
import streamlit as st
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.bcolors import bcolors
from src.prompts import prompts
from src.routes import getConversationById, getConversationsByProjectId, sendMessageToLlm
from src.utils import extract_json_object, filter_insights

st.set_page_config(
    page_title="Tolk.ai • Conversation Analysis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title('🔮 :violet[Tolk.ai] • Conversation Analysis')

ProjectConversationsTab, ConversationTab, DatasetFileTab = st.tabs(["🤖 Project Conversations", "💬 Conversation", "📄 Dataset File"])

with ProjectConversationsTab:
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
            

with ConversationTab:
    st.header("Conversation Analysis")
    projectId = st.text_input("Enter a ConversationId:", "e51255e3-2790-4ab7-964c-6f898f7e00f7")


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
"Write your prompt here",
prompts[3],
height=200,
)

azureOpenAiApiModelChoice = azureOpenAiApiCredentials.keys()
modelCol, analyzeCol = st.columns(2)
with modelCol:
    azureOpenAiApiModel = st.selectbox(
        "Select a promptId",
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

        result = {}
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

#    "issue_summary":(string),
#    "conversation_objective":(string),
#    "context_of_request":(string),
#    "language_and_tone":("formal"|"informal"|"colloquial"|"slang"|"jargon"|"vulgar"|"standard"|"literary"|"technical"),
#    "client_communication_preferences":("email"|"phone calls"|"in-person"|"text messages"|"social media"|"customer support"|"agent ai"),``
                    
                    st.write(f"📝 **Issue Summary**: {llmResponseJson['issue_summary']}")
                    st.write(f"🎯 **Conversation Objective**: {llmResponseJson['conversation_objective']}")
                    st.write(f"🔍 **Context of Request**: {llmResponseJson['context_of_request']}")
                    st.write(f"🗣️ **Language and Tone**: {llmResponseJson['language_and_tone']}")
                    st.write(f"📞 **Client Communication Preferences**: {llmResponseJson['client_communication_preferences']}")

                    # ranger les metric en colone de 3
                    col1, col2, col3 = st.columns(3)
                    col1.metric(llmResponseJson["client_expectations"]["name"], llmResponseJson["client_expectations"]["value"], llmResponseJson["client_expectations"]["delta"])
                    col2.metric(llmResponseJson["client_sentiment"]["name"], llmResponseJson["client_sentiment"]["value"], llmResponseJson["client_sentiment"]["delta"])
                    col3.metric(llmResponseJson["service_quality"]["name"], llmResponseJson["service_quality"]["value"], llmResponseJson["service_quality"]["delta"])

                    col4, col5, col6 = st.columns(3)
                    col4.metric(llmResponseJson["request_complexity_level"]["name"], llmResponseJson["request_complexity_level"]["value"], llmResponseJson["request_complexity_level"]["delta"])
                    col5.metric(llmResponseJson["situation_sensitivity"]["name"], llmResponseJson["situation_sensitivity"]["value"], llmResponseJson["situation_sensitivity"]["delta"])
                    col6.metric(llmResponseJson["request_urgency_level"]["name"], llmResponseJson["request_urgency_level"]["value"], llmResponseJson["request_urgency_level"]["delta"])

                    col7, col8, col9 = st.columns(3)
                    col7.metric(llmResponseJson["assistant_knowledge_gap"]["name"], llmResponseJson["assistant_knowledge_gap"]["value"], llmResponseJson["assistant_knowledge_gap"]["delta"])
                    col8.metric(llmResponseJson["proposed_solutions_relevance"]["name"], llmResponseJson["proposed_solutions_relevance"]["value"], llmResponseJson["proposed_solutions_relevance"]["delta"])
                    col9.metric(llmResponseJson["solutions_adaptability"]["name"], llmResponseJson["solutions_adaptability"]["value"], llmResponseJson["solutions_adaptability"]["delta"])

                    col10, col11, col12 = st.columns(3)
                    col10.metric(llmResponseJson["confidentiality_level"]["name"], llmResponseJson["confidentiality_level"]["value"], llmResponseJson["confidentiality_level"]["delta"])
                    col11.metric(llmResponseJson["issue_identification_ability"]["name"], llmResponseJson["issue_identification_ability"]["value"], llmResponseJson["issue_identification_ability"]["delta"])
                    col12.metric(llmResponseJson["use_of_customer_data"]["name"], llmResponseJson["use_of_customer_data"]["value"], llmResponseJson["use_of_customer_data"]["delta"])

                    col13, col14, col15 = st.columns(3)
                    col13.metric(llmResponseJson["agent_empathetic_approach_use"]["name"], llmResponseJson["agent_empathetic_approach_use"]["value"], llmResponseJson["agent_empathetic_approach_use"]["delta"])
                    col14.metric(llmResponseJson["negative_publicity_risk"]["name"], llmResponseJson["negative_publicity_risk"]["value"], llmResponseJson["negative_publicity_risk"]["delta"])
                    col15.metric(llmResponseJson["response_accuracy"]["name"], llmResponseJson["response_accuracy"]["value"], llmResponseJson["response_accuracy"]["delta"])

                    col16, col17 = st.columns(2)
                    col16.metric(llmResponseJson["problem_resolution_rate"]["name"], llmResponseJson["problem_resolution_rate"]["value"], llmResponseJson["problem_resolution_rate"]["delta"])
                    col17.metric(llmResponseJson["commercial_opportunities"]["name"], llmResponseJson["commercial_opportunities"]["value"], llmResponseJson["commercial_opportunities"]["delta"])

                    

                    for message in conversationMessages["history"]:
                        if message["sender"] == projectId:
                            st.chat_message("assistant").write(message["content"]["text"])
                        else:
                            st.chat_message("user").write(message["content"]["text"])
                    # st.write(conversationMessages)
                # try:
                #     conversationMessages = getConversationById(new_projectId, conversationId)
                # except Exception as e:
                #     st.error(f"❌ Error analyzing conversation {conversationId}: {e}")
                #     st.stop()
                # result[conversationId] = conversationMessages["conversationId"]
                # messages=[{"role": "system", "content": llmPrompt}]
                # for message in conversationMessages["history"]:
                #     if message["sender"] == new_projectId:
                #         messages.append({"role": "assistant", "content": message["content"]["text"]})
                #     else:
                #         messages.append({"role": "user", "content": message["content"]["text"]})
                # print(f"{bcolors.OKBLUE}        🤖 Sending conversation to {new_azureOpenAiApiModel} with prompt {new_promptId}...{bcolors.ENDC}")
                # try:
                #     llmResponse = sendMessageToLlm(messages, deployment_name, client)
                # except Exception as e:
                #     st.error(f"❌ Error sending conversation to {new_azureOpenAiApiModel} with prompt {new_promptId}: {e}")
                #     st.stop()
                # print(f"{bcolors.OKCYAN}        🔮 Analyzing LLM format response{bcolors.ENDC}")
                # try:
                #     llmResponseJson = extract_json_object(llmResponse)
                # except Exception as e:
                #     st.error(f"❌ Error analyzing LLM response: {e}")
                #     st.stop()
                # result[conversationId] = llmResponseJson
                indexConversation += 1
        except KeyError:
            st.error("❌ Error: Invalid projectId")
            st.stop()
            
    except KeyError:
        st.error("Invalid promptId")
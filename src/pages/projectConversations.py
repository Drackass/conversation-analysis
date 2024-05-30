import streamlit as st
import datetime
from src.prompts import prompts
from src.azureOpenAiApiCredentials import azureOpenAiApiCredentials
from src.routes import getConversationById, getConversationsByProjectId, sendMessageToLlm
from src.utils import extract_json_object
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
        label="Write your prompt here",
        value=prompts[4],
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

                        # same with progress bar exemple:
                        # progress_text = "Operation in progress. Please wait."
                        # my_bar = st.progress(50, text=progress_text)

                        # st.progress(llmResponseJson["client_expectations"]["delta"], llmResponseJson["client_expectations"]["name"])
                        # st.progress(llmResponseJson["client_sentiment"]["delta"], llmResponseJson["client_sentiment"]["name"])
                        # st.progress(llmResponseJson["service_quality"]["delta"], llmResponseJson["service_quality"]["name"])
                        # st.progress(llmResponseJson["request_complexity_level"]["delta"], llmResponseJson["request_complexity_level"]["name"])
                        # st.progress(llmResponseJson["situation_sensitivity"]["delta"], llmResponseJson["situation_sensitivity"]["name"])
                        # st.progress(llmResponseJson["request_urgency_level"]["delta"], llmResponseJson["request_urgency_level"]["name"])
                        # st.progress(llmResponseJson["assistant_knowledge_gap"]["delta"], llmResponseJson["assistant_knowledge_gap"]["name"])
                        # st.progress(llmResponseJson["proposed_solutions_relevance"]["delta"], llmResponseJson["proposed_solutions_relevance"]["name"])
                        # st.progress(llmResponseJson["solutions_adaptability"]["delta"], llmResponseJson["solutions_adaptability"]["name"])
                        # st.progress(llmResponseJson["confidentiality_level"]["delta"], llmResponseJson["confidentiality_level"]["name"])
                        # st.progress(llmResponseJson["issue_identification_ability"]["delta"], llmResponseJson["issue_identification_ability"]["name"])
                        # st.progress(llmResponseJson["use_of_customer_data"]["delta"], llmResponseJson["use_of_customer_data"]["name"])
                        # st.progress(llmResponseJson["agent_empathetic_approach_use"]["delta"], llmResponseJson["agent_empathetic_approach_use"]["name"])
                        # st.progress(llmResponseJson["negative_publicity_risk"]["delta"], llmResponseJson["negative_publicity_risk"]["name"])
                        # st.progress(llmResponseJson["response_accuracy"]["delta"], llmResponseJson["response_accuracy"]["name"])
                        # st.progress(llmResponseJson["problem_resolution_rate"]["delta"], llmResponseJson["problem_resolution_rate"]["name"])
                        # st.progress(llmResponseJson["commercial_opportunities"]["delta"], llmResponseJson["commercial_opportunities"]["name"])




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
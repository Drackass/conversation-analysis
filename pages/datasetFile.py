from io import StringIO
import json
import streamlit as st
import pandas as pd
from src.routes import getConversationById, sendCompletionToLlm, sendMessageToLlm
from src.utils import extract_json_object, filter_dataframe
from src.prompts import prompts
import openai
from src.components.sidebar import sidebar
import asyncio
import streamlit as st
from src.routes import getConversationsByProjectId, getConversationById, sendMessageToLlm, sendCompletionToLlm, generateReport
from src.utils import flatten_json, extract_json_structure, formalize_messages, extract_json_object
from src.prompts import prompts, context, jsonStructurePrompt, reportPrompt, refJsonStructurePrompt, protoprompt
import openai
import pandas as pd
from src.components.sidebar import sidebar
import json
import asyncio
import datetime

sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "📄 Dataset File Analysis")

# exemple de structure a avoir pour le fichier csv

# Fonction pour vérifier la structure du dataframe
def verify_structure(df):
    required_columns = ['ID', 'ROLE', 'CONTENT','DATE']
    if all(column in df.columns for column in required_columns):
        return True
    else:
        return False

# Fonction pour structurer les données en JSON par ID
def structure_data(df):
    structured_data = []
    for _, row in df.iterrows():
        id_ = int(row['ID'])
        role = str(row['ROLE'])
        content = str(row['CONTENT'])
        date = str(row['DATE'])
        conversation = next((conv for conv in structured_data if conv['id'] == id_), None)
        if conversation is None:
            conversation = {'id': id_, 'history': [], 'date': date}
            structured_data.append(conversation)
        conversation['history'].append({'role': role, 'content': content})
    return structured_data

# Chargement du fichier CSV
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dataset Preview:")
    st.write(df)
    
    # Vérification de la structure
    if verify_structure(df):
        # Structuration des données en JSON
        json_data = structure_data(df)
        # st.json(json_data)
        conversations = json_data
    else:
        st.error("The file structure is incorrect. Please ensure it has 'ID', 'ROLE', and 'CONTENT' columns.")

with st.expander('🔎 Analysis Prompts'):
    customPrompt = st.text_area(
            label="Enter a prompt to analyze the conversations:",
            value=protoprompt,
            # value=prompts[6],
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
        index=1,
        label_visibility="collapsed",
    )

# if 'btn_analyze_clicked' not in st.session_state:
#     st.session_state['btn_analyze_clicked'] = False

btnAnalyze= st.button(
    "Analyze",
    use_container_width=True,
    type="primary",
    disabled=uploaded_file is None,
    )

# if btnAnalyze:
#     st.session_state['btn_analyze_clicked'] = True

client_asynchrone = openai.AsyncOpenAI(api_key=st.secrets["OPENAI_API_KEY"])
client_synchrone = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
if btnAnalyze:
    st.divider()
    refJsonFormat = ""
    with st.spinner(f"Sending a request to {OpenAiApiModel} to get the structure of the analysis..."):
        try:
            llmResponse= sendCompletionToLlm(f"{refJsonStructurePrompt}\n{customPrompt}", OpenAiApiModel, client_synchrone)

            try:
                extractedJsonStructure = extract_json_object(llmResponse)
                refJsonStructure = extract_json_structure(extractedJsonStructure)
                st.success(f"Received the structure of the analysis from {OpenAiApiModel} successfully", icon='✅')
            except Exception as e:
                st.error(f"❌ Error Parsing {OpenAiApiModel} response in json: {e}")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error Sending a request to {OpenAiApiModel} to get the structure of the analysis: {e}")
            st.stop()

    # st.write(refJsonStructure)
    
    async def conversationAnalysis(conversation):
        error = ""
        analysis = st.empty()
        conversationId = conversation["id"]
        

        with analysis.status(f"🔎 {conversationId}. Conversation Analysis", expanded=False):
            st.write("analyzing conversation...")

            try:
                analysisPrompt = f"{context}\n{customPrompt}\n\n{jsonStructurePrompt}\n\n```json\n{json.dumps(refJsonStructure, indent=2)}\n```"
                messages = [{"role": "system", "content": analysisPrompt}, *conversation["history"]]
                # st.json(messages)
                

                st.write(f"Sending conversation to {OpenAiApiModel}...")
                try:
                    llmResponse = await sendMessageToLlm(messages, OpenAiApiModel, client_asynchrone)
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
        else:
            with st.expander(f"🔮 {conversationId}. Conversation Analysis"):
                flatData = flatten_json(llmResponseJson)
                # st.write(flatData)

                formatedMessages = formalize_messages(messages)
                flatData["conversation"] = formatedMessages

                # format 'dd/mm/yyyy'
                date_str = conversation["date"]

                # i use is_datetime64_any_dtype to check the date so convert this in the correct format
                date = pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
                
                flatData["date"] = date

                totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)

                totalInsightCol.write(f"🔍 Insights :blue-background[**{len(llmResponseJson)}**]")
                totalColumnCol.write(f"➡️ Columns :blue-background[**{len(flatData)}**]")
                totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
                TotalMessageCol.write(f"💬 Messages :blue-background[**{len(conversation['history'])}**]")

                formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}

                dataConversation = {}
                dataConversation[conversationId] = formatedFlatData

                dfConversations = pd.DataFrame(dataConversation).T

                st.write(dfConversations)

                st.divider()
                for message in conversation["history"]:
                    # if message["sender"] == projectId:
                    #     st.chat_message("assistant").write(message["content"]["text"])
                    # else:
                    #     st.chat_message("user").write(message["content"]["text"])

                    if message["role"] == "assistant":
                        st.chat_message("assistant").write(message["content"])
                    else:
                        st.chat_message("user").write(message["content"])


        analysisResultsFormated[conversationId] = formatedFlatData
        analysisResults[conversationId] = llmResponseJson

    analysisResultsFormated = {}
    analysisResults = {}
    flatData = {}

    async def conversationsAnalysisTasks():
        global analysisResultsFormated, analysisResults, flatData, refJsonStructure
        tasks = []
        for conversation in conversations:
            task = conversationAnalysis(conversation)
            tasks.append(task)
        await asyncio.gather(*tasks)

    asyncio.run(conversationsAnalysisTasks())

    with st.expander(f'📚 Report all conversations in the imported file'):
        formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}

        csvformatedjson = pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)
        df = pd.read_csv(StringIO(csvformatedjson))
        filter_dataframe(df)

        st.divider()

        reportPromptWithVerbatim = f"{customPromptReport}\n\n```json\n{json.dumps(analysisResults, indent=2)}\n```"
        reportContainer = st.container(border=True).empty()

        generateReport(reportPromptWithVerbatim, OpenAiApiModelReport, client_synchrone, reportContainer)

        # with st.popover("Copy JSON"):
        #     st.code(json.dumps(analysisResults, indent=2), language="JSON")

        # st.divider()

        # csvformatedjson = pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)
        # df = pd.read_csv(StringIO(csvformatedjson))
        # filter_dataframe(df)

    st.toast("Analysis Completed", icon="✅")
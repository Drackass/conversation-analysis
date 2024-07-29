from io import StringIO
import json
import streamlit as st
import pandas as pd
from src.components.sidebar import sidebar
import asyncio
from src.routes import sendMessageToLlm, sendCompletionToLlm, generateReport
from src.utils import flatten_json, extract_json_structure, formalize_messages, extract_json_object, filter_dataframe, filter_chart
from src.prompts import prompts, context, jsonStructurePrompt, reportPrompt, refJsonStructurePrompt, protoprompt
import openai
import altair as alt
from vega_datasets import data

import tiktoken
from src.other.embeddings_utils import get_embedding
import numpy as np
from sklearn.manifold import TSNE
from ast import literal_eval
import plotly.express as px
from src.other.chart import generate_embedding, filter_similar_embeddings, generate_tsne_chart, normalize_themes, generate_bubble_chart_from_prompt, generate_bubble_chart, generate_custom_chart, getDfWithEmbeding
import threading

sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "📄 Dataset File Analysis")

@st.experimental_fragment
def generateChart(dfWithEmbedding):
    dataframe = pd.read_csv(StringIO(dfWithEmbedding.to_csv(index=False)))
    matrix = np.array(dataframe.embedding.apply(literal_eval).to_list())
    num_samples = len(dataframe)
    perplexity = min(15, num_samples - 1)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    dataframe['x'] = vis_dims[:, 0]
    dataframe['y'] = vis_dims[:, 1]
    fig = px.scatter(dataframe, x='x', y='y', color='categorie', hover_data=['id'], size='count')
    st.plotly_chart(fig, on_select="rerun", key="my_chart" )

def verify_structure(df):
    required_columns = ['ID', 'ROLE', 'CONTENT','DATE']
    if all(column in df.columns for column in required_columns):
        return True
    else:
        return False

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

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dataset Preview:")
    st.write(df)
    
    if verify_structure(df):
        json_data = structure_data(df)
        conversations = json_data
    else:
        st.error("The file structure is incorrect. Please ensure it has 'ID', 'ROLE', and 'CONTENT' columns.")

with st.expander('🔎 Analysis Prompts'):
    customPrompt = st.text_area(
            label="Enter a prompt to analyze the conversations:",
            value=protoprompt,
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

with st.expander('⚙️ Advanced Settings'):
    showReport = st.checkbox("show report", value=True)
    showthemesChart = st.checkbox("show themes chart", value=True)
    showconversationChart = st.checkbox("show conversation chart", value=True)
    showbubbleChart = st.checkbox("show bubble chart", value=True)
    showIndividualConversationsAnalysis = st.checkbox("show individual conversations", value=True)
    showCustomChart = st.checkbox("show custom chart", value=True)

btnAnalyze= st.button(
    "Analyze",
    use_container_width=True,
    type="primary",
    disabled=uploaded_file is None,
    )

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


    # Initialize the progress bar
    progress_bar = st.progress(0, text="Analyzing Conversations...")
    lock = threading.Lock()

    async def conversationAnalysis(conversation, progress, total_conversations):
        conversationId = conversation["id"]        

        try:
            analysisPrompt = f"{context}\n{customPrompt}\n\n{jsonStructurePrompt}\n\n```json\n{json.dumps(refJsonStructure, indent=2)}\n```"
            messages = [{"role": "system", "content": analysisPrompt}, *conversation["history"]]

            try:
                llmResponse = await sendMessageToLlm(messages, OpenAiApiModel, client_asynchrone)
                try:
                    llmResponseJson = extract_json_object(llmResponse)
                except Exception as e:
                    error = f"Error Parsing {OpenAiApiModel} response in json: {e}"

            except Exception as e:
                error = f"Error Sending conversation **{conversationId}** to {OpenAiApiModel}: {e}"
        
        except Exception as e:
            error = f"Error Fetching conversation **{conversationId}**: {e}"

        flatData = flatten_json(llmResponseJson)
        formatedMessages = formalize_messages(messages)
        flatData["conversation"] = formatedMessages
        date_str = conversation["date"]
        date = pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')
        flatData["date"] = date
        flatData["id"] = conversationId
        formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}
        dataConversation = {}
        dataConversation[conversationId] = formatedFlatData
        dfConversations = pd.DataFrame(dataConversation).T
        analysisResultsFormated[conversationId] = formatedFlatData
        analysisResults[conversationId] = llmResponseJson
        analysisResultsJson[conversationId] = {
            "summary": "Conversation Analysis",
            "analysisData": dfConversations,
            "conversation": conversation["history"]
        }

        with lock:
            progress[0] += 1
            progress_bar.progress(progress[0] / total_conversations, text=f"Analyzing Conversation {progress[0]}/{total_conversations}")

    analysisResultsFormated = {}
    analysisResults = {}
    flatData = {}
    analysisResultsJson = {}

    async def conversationsAnalysisTasks():
        global analysisResultsFormated, analysisResults, flatData, refJsonStructure, analysisResultsJson
        total_conversations = len(conversations)
        progress = [0]
        tasks = []
        for conversation in conversations:
            task = conversationAnalysis(conversation, progress, total_conversations)
            tasks.append(task)
        await asyncio.gather(*tasks)
        progress_bar.empty()

    asyncio.run(conversationsAnalysisTasks())

    with st.expander(f'📚 Conversation analysis final report'):
        formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}

        if showReport:
            reportPromptWithVerbatim = f"{customPromptReport}\n\n```json\n{json.dumps(analysisResults, indent=2)}\n```"
            reportContainer = st.container(border=True).empty()
            generateReport(reportPromptWithVerbatim, OpenAiApiModelReport, client_synchrone, reportContainer)
            st.divider()

        csvformatedjson = pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)
        df = pd.read_csv(StringIO(csvformatedjson))
        # filter_dataframe(df)

        # filter conversation
        st.write("📊 Filter conversations:")
        with st.spinner('Wait for it...'):
            dfCustomChart = getDfWithEmbeding(df)
            csvformatedjson = pd.DataFrame(dfCustomChart).to_csv(index=False)
            df = pd.read_csv(StringIO(csvformatedjson))
            filter_chart(df)

        if showthemesChart:
            st.write("📊 Themes Chart:")
            with st.spinner('Wait for it...'):
                base_data = df.copy()
                df_themes = base_data["theme"].str.lower().str.strip().value_counts().reset_index()
                df_themes.columns = ["theme", "count"]
                df_with_embedding = generate_embedding(df_themes, "theme")
                df_with_embedding = filter_similar_embeddings(df_with_embedding)
                csv_data = df_with_embedding.to_csv(index=False)
                df_with_embedding = pd.read_csv(StringIO(csv_data))
                fig = generate_tsne_chart(df_with_embedding, 'theme', size_column='count')
                st.plotly_chart(fig, on_select="rerun", key="my_chart_1")

        if showconversationChart:
            st.write("📊 Conversation Chart:")
            with st.spinner('Wait for it...'):
                base_data = df.copy()
                base_data['theme'] = normalize_themes(base_data['theme'])
                df_with_embedding = generate_embedding(base_data, "conversation")
                csv_data = df_with_embedding.to_csv(index=False)
                df_with_embedding = pd.read_csv(StringIO(csv_data))
                fig = generate_tsne_chart(df_with_embedding, 'theme')
                st.plotly_chart(fig, on_select="rerun", key="my_chart_2")

        if showbubbleChart:
            st.write("📊 Bubble Chart:")
            with st.spinner('Wait for it...'):
                data = df.copy()
                llm_response_json = generate_bubble_chart_from_prompt(data, st.secrets["OPENAI_API_KEY"])
                generate_bubble_chart(llm_response_json)

        if showCustomChart:
            st.write("📊 Custom Chart:")
            with st.spinner('Wait for it...'):
            # dfCustomChart = getDfWithEmbeding(df)
            # generate_custom_chart(dfCustomChart)
                dfCustomChart = getDfWithEmbeding(df)
                csvformatedjson = pd.DataFrame(dfCustomChart).to_csv(index=False)
                df = pd.read_csv(StringIO(csvformatedjson))
                filter_chart(df)



    if showIndividualConversationsAnalysis:
        st.divider()

        sorted_analysis_results = sorted(analysisResultsJson.items(), key=lambda x: x[0])
        for analysis, result in sorted_analysis_results:
            with st.expander(f"🔮 {analysis}.  {result['summary']}"):
                totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)
                totalInsightCol.write(f"🔍 Insights :blue-background[**{len(analysisResultsJson)}**]")
                totalColumnCol.write(f"➡️ Columns :blue-background[**{len(df.columns)}**]")
                totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
                TotalMessageCol.write(f"💬 Messages :blue-background[**{len(result['conversation'])}**]")
                st.dataframe(result['analysisData'])

                for message in result["conversation"]:
                    if message["role"] == "assistant":
                        st.chat_message("assistant").write(message["content"])
                    else:
                        st.chat_message("user").write(message["content"])


    st.toast("Analysis Completed", icon="✅")
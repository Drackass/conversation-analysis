
import asyncio
import threading
import streamlit as st
import pandas as pd

from src.shared.prompts import getAnalysisPrompt

from src.shared.genericUtils import extractJsonObjectFromText
from src.shared.openaiUtils import sendMessageToLlm, messagesToString
from src.shared.genericUtils import flattenJson

def extractJsonConversationsDataFromTable(df):
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


def extractJsonGeniiConversationsDataFromTable(df):
    structured_data = []
    for _, row in df.iterrows():
        conversationId = str(row['conversationId'])
        date = str(row['date'])
        content = str(row['content.value'])
        try:
            parsed_date = pd.to_datetime(date, format='%b %d, %Y @ %H:%M:%S.%f')
            formatted_date = parsed_date.strftime('%d/%m/%Y')
        except Exception as e:
            st.error(f"Error parsing date '{date}': {e}")
            continue
        conversation = next((conv for conv in structured_data if conv['id'] == conversationId), None)
        if conversation is None:
            conversation = {'id': conversationId, 'history': [], 'date': formatted_date}
            structured_data.append(conversation)
        conversation['history'].append({'role': 'user', 'content': content})
    return structured_data


def extractMessagesFromGeniiHistory(projectId, history):
    messages = []
    for message in history:
        if message["sender"] == projectId:
            messages.append({"role": "assistant", "content": message["content"]["text"]})
        else:
            messages.append({"role": "user", "content": message["content"]["text"]})
    return messages

async def conversationAnalysis(conversation, progress, total_conversations, lock, progress_bar, insightsToAnalysePrompt, referenceJsonStructureTypes, OpenAiApiModelAnalysis, analysisResultsFormated, analysisResults, analysisResultsJson):
    conversationId = conversation["id"]        

    try:
        analysisPrompt = getAnalysisPrompt(insightsToAnalysePrompt, referenceJsonStructureTypes)
        messages = [{"role": "system", "content": analysisPrompt}, *conversation["history"]]

        try:
            llmResponse = await sendMessageToLlm(messages, OpenAiApiModelAnalysis, asyncronous=True)
            try:
                llmResponseJson = extractJsonObjectFromText(llmResponse)
            except Exception as e:
                error = f"Error Parsing {OpenAiApiModelAnalysis} response in json: {e}"

        except Exception as e:
            error = f"Error Sending conversation **{conversationId}** to {OpenAiApiModelAnalysis}: {e}"
    
    except Exception as e:
        error = f"Error Fetching conversation **{conversationId}**: {e}"
    
    if "error" in locals():
        st.error(error)
        return

    flatData = flattenJson(llmResponseJson)
    flatData.update({
        "conversation": messagesToString(messages),
        "date": pd.to_datetime(conversation["date"], format='%d/%m/%Y').strftime('%Y-%m-%d'),
        "id": conversationId
    })
    formatedFlatData = {key.replace("_", " ").replace("-", " > "): value for key, value in flatData.items()}
    analysisResultsFormated[conversationId] = formatedFlatData
    analysisResults[conversationId] = llmResponseJson
    analysisResultsJson[conversationId] = {
        "summary": conversation["summary"] if "summary" in conversation else "Conversation Analysis",
        "analysisData": formatedFlatData,
        # "analysisData": pd.DataFrame([formatedFlatData], index=[conversationId]),
        "conversation": conversation["history"]
    }

    with lock:
        progress[0] += 1
        progress_bar.progress(progress[0] / total_conversations, text=f"Analyzing Conversation {progress[0]}/{total_conversations}")

async def conversationsAnalysisTasks(jsonConversationsData, insightsToAnalysePrompt, referenceJsonStructureTypes, OpenAiApiModelAnalysis):
    progress_bar = st.progress(0, text="Analyzing Conversations...")
    total_conversations = len(jsonConversationsData)
    progress = [0]
    tasks = []
    analysisResultsFormated = {}
    analysisResults = {}
    analysisResultsJson = {}
    lock = threading.Lock()
    
    for conversation in jsonConversationsData:
        task = conversationAnalysis(conversation, progress, total_conversations, lock, progress_bar, insightsToAnalysePrompt, referenceJsonStructureTypes, OpenAiApiModelAnalysis, analysisResultsFormated, analysisResults, analysisResultsJson)
        tasks.append(task)
    await asyncio.gather(*tasks)
    st.success(f"{total_conversations} Conversations Analyzed", icon='✅')
    progress_bar.empty()
    return analysisResultsFormated, analysisResults, analysisResultsJson
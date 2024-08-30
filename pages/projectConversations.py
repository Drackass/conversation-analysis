import datetime
from io import StringIO
import streamlit as st
import pandas as pd
import asyncio

from src.components.sidebar import Sidebar
from src.components.filterDataframe import FilterDataframe
from src.components.analysisSettings import AnalysisSettings

from src.shared.prompts import getStructureJsonPrompt, getReportWithVerbatimPrompt

from src.shared.openaiUtils import sendCompletionToLlm, generateReport
from src.shared.genericUtils import extractStructureTypesFromObject, extractJsonObjectFromText
from src.shared.openaiUtils import generateRerankedConversations
from src.shared.chartUtils import generateBubbleChart
from src.shared.embeddingUtils import getDataframeWithEmbeddings, getDataframeWithEmbeddingsTask, getPointsForTSNE
from src.shared.conversationsUtils import conversationsAnalysisTasks
from src.shared.geniiUtlis import authenticate, getAllUsers, getConversationsInfosByProjectId, getConversationsDataTasks, get_access_token, get_refresh_token

# @st.experimental_fragment
# def showIndividualConversationsAnalysis(conversationsData, analysisResultsJson):
    

def main():
    authenticate()
        
    allUsers = getAllUsers()
    projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], key="projectIdConversations")["id"]

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
                options= range(1, 201),
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

    insightsToAnalysePrompt, openAiApiModelAnalysis, reportPrompt, OpenAiApiModelReport, showReport, showbubbleChart, showIndividualConversationsAnalysis, btnAnalyze, allowToFilterWithChart = AnalysisSettings(False)

    if btnAnalyze:
        st.divider()
        with st.spinner(f"Sending a request to {openAiApiModelAnalysis} to get the structure of the analysis..."):
            try:
                llmResponse= sendCompletionToLlm(getStructureJsonPrompt(insightsToAnalysePrompt), openAiApiModelAnalysis, asyncronous=False)
                try:
                    extractedJsonObject = extractJsonObjectFromText(llmResponse)
                    referenceJsonStructureTypes = extractStructureTypesFromObject(extractedJsonObject)
                    st.success(f"Received the structure of the analysis from {openAiApiModelAnalysis} successfully", icon='✅')
                except Exception as e:
                    st.error(f"❌ Error Parsing {openAiApiModelAnalysis} response in json: {e}")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Error Sending a request to {openAiApiModelAnalysis} to get the structure of the analysis: {e}")
                st.stop()
                
        with st.spinner(f"Fetching {conversationLimit[0]} Genii conversations Infos from project {projectId}..."):
            conversationsInfos = getConversationsInfosByProjectId(projectId, params)

        conversationsData = []
        batch_size = 10
        num_batches = len(conversationsInfos["data"]) // batch_size + 1

        for i in range(num_batches):
            batch = conversationsInfos["data"][i * batch_size : (i + 1) * batch_size]
            batch_conversations_data = asyncio.run(getConversationsDataTasks(batch, projectId))
            conversationsData.extend(batch_conversations_data)

        # st.success(f"Fetched {len(conversationsData)} Genii Conversations data from project {projectId} successfully", icon='✅')
        
        # conversationsData = asyncio.run(getConversationsDataTasks(conversationsInfos["data"], projectId))

        analysisResultsFormated, analysisResults, analysisResultsJson = asyncio.run(conversationsAnalysisTasks(conversationsData, insightsToAnalysePrompt, referenceJsonStructureTypes, openAiApiModelAnalysis))

        with st.expander(f'📚 Conversation analysis final report', expanded=True):

            analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)))

            if showReport:
                generateReport(getReportWithVerbatimPrompt(reportPrompt, analysisResults), OpenAiApiModelReport)

            st.write("📊 Conversations Analysis:")
            with st.spinner('Wait for it...'):
                if allowToFilterWithChart:
                    dataframeWithEmbeddings = asyncio.run(getDataframeWithEmbeddingsTask(analysisResultsFormatedForReport, 'conversation'))
                    analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(dataframeWithEmbeddings).to_csv(index=False)))
                    analysisResultsFormatedForReport = getPointsForTSNE(analysisResultsFormatedForReport)
                FilterDataframe(analysisResultsFormatedForReport, allowToFilterWithChart)

            if showbubbleChart:
                st.write("📊 Bubble Chart:")
                with st.spinner('Wait for it...'):
                    data = analysisResultsFormatedForReport.copy()
                    llm_response_json = generateRerankedConversations(data)
                    generateBubbleChart(llm_response_json)
    
        

        if showIndividualConversationsAnalysis:
            st.divider()

            sorted_analysis_results = sorted(analysisResultsJson.items(), key=lambda x: x[0])
            for analysis, result in sorted_analysis_results:
                with st.expander(f"🔮 {analysis}.  {result['summary']}"):
                    dfAnalytics = result['analysisData'].copy()
                    dfAnalytics = dfAnalytics.drop(columns=[col for col in ["id", "conversation", "date"] if col in dfAnalytics.columns])
                    totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)
                    totalInsightCol.write(f"🔍 Insights :blue-background[**{len(dfAnalytics.columns)}**]")
                    totalColumnCol.write(f"➡️ Columns :blue-background[**{len(result['analysisData'].columns)}**]")
                    totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
                    TotalMessageCol.write(f"💬 Messages :blue-background[**{len(result['conversation'])}**]")
                    st.dataframe(result['analysisData'])

                    for message in result["conversation"]:
                        if message["role"] == "assistant":
                            st.chat_message("assistant").write(message["content"])
                        else:
                            st.chat_message("user").write(message["content"])

        st.toast("Analysis Completed", icon="✅")

Sidebar("Genii • Conversation Analysis | Project Conversations", '🧞 :violet[Genii] • Conversation Analysis', "🔮 Project Conversations Analysis")
main()
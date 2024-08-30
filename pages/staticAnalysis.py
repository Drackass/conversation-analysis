from io import StringIO
import streamlit as st
import pandas as pd
import asyncio

from src.components.sidebar import Sidebar
from src.components.filterDataframe import FilterDataframe
from src.components.analysisSettings import AnalysisSettings

from src.shared.prompts import INITIALS_INSIGHTS_TEMPLATE_PROMPT, INSIGHTS_TEMPLATE_PROMPT, getStructureJsonPrompt, getReportWithVerbatimPrompt

from src.shared.openaiUtils import OPENAI_API_MODELS, sendCompletionToLlm, generateReport
from src.shared.genericUtils import extractStructureTypesFromObject, extractJsonObjectFromText, verifyStructureTable
from src.shared.openaiUtils import generateRerankedConversations
from src.shared.chartUtils import generateBubbleChart
from src.shared.embeddingUtils import getDataframeWithEmbeddings, getPointsForTSNE, getDataframeWithEmbeddingsTask
from src.shared.conversationsUtils import extractJsonGeniiConversationsDataFromTable, conversationsAnalysisTasks
from src.shared.staticData import CONVERSATIONS_DATA, REFERENCE_STRUCTURE_ANALYSIS, ANALYSIS_RESULTS_FORMATED, REPORT_ANALYSIS, ANALYSIS_RESULTS, ANALYSIS_RESULTS_JSON, JSON_DATAFRAME_WITH_EMBEDDINGS, REORDERED_TOPICS

def main():

    st.write("Dataset Preview:")
    staticConversationsDataDataframe = []
    for conv in CONVERSATIONS_DATA:
        conv_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conv["history"]])
        staticConversationsDataDataframe.append({"id": conv["id"], "conversation": conv_text})

    st.dataframe(pd.DataFrame(staticConversationsDataDataframe))

    jsonConversationsData = CONVERSATIONS_DATA

    insightsToAnalysePrompt = INSIGHTS_TEMPLATE_PROMPT

    insightsToAnalysePrompt = f"{INITIALS_INSIGHTS_TEMPLATE_PROMPT}\n{insightsToAnalysePrompt}"

    openAiApiModelAnalysis = OPENAI_API_MODELS[0]

    showReport = True
    allowToFilterWithChart = True
    showbubbleChart = True
    showIndividualConversationsAnalysis = True

    st.divider()
    with st.spinner(f"Get the structure of the analysis..."):
        try:
            llmResponse = REFERENCE_STRUCTURE_ANALYSIS

            try:
                extractedJsonObject = extractJsonObjectFromText(llmResponse)
                referenceJsonStructureTypes = extractStructureTypesFromObject(extractedJsonObject)
                st.success(f"Received the structure of the analysis successfully", icon='✅')
            except Exception as e:
                st.error(f"❌ Error Parsing {openAiApiModelAnalysis} response in json: {e}")
                st.stop()
        except Exception as e:
            st.error(f"❌ Error Sending a request to {openAiApiModelAnalysis} to get the structure of the analysis: {e}")
            st.stop()

    analysisResultsFormated = ANALYSIS_RESULTS_FORMATED
    analysisResults = ANALYSIS_RESULTS
    analysisResultsJson = ANALYSIS_RESULTS_JSON

    with st.expander(f'📚 Conversation analysis final report', expanded=True):

        analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)))

        if showReport:
            reportContainer = st.container(border=True).empty()
            reportContainer.markdown(REPORT_ANALYSIS)
            with st.popover("Copy"):
                st.code(REPORT_ANALYSIS, language="markdown")


        st.write("📊 Conversations Analysis:")
        with st.spinner('Wait for it...'):
            if allowToFilterWithChart:
                dataframeWithEmbeddings = pd.DataFrame(JSON_DATAFRAME_WITH_EMBEDDINGS)
                analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(dataframeWithEmbeddings).to_csv(index=False)))
                analysisResultsFormatedForReport = getPointsForTSNE(analysisResultsFormatedForReport)
            FilterDataframe(analysisResultsFormatedForReport, allowToFilterWithChart)

        if showbubbleChart:
            st.write("📊 Bubble Chart:")
            with st.spinner('Wait for it...'):
                data = analysisResultsFormatedForReport.copy()
                llm_response_json = REORDERED_TOPICS
                generateBubbleChart(llm_response_json)

    if showIndividualConversationsAnalysis:
        st.divider()
        sorted_analysis_results = sorted(analysisResultsJson.items(), key=lambda x: x[0])
        for analysis, result in sorted_analysis_results:
            with st.expander(f"🔮 {analysis}.  {result['summary']}"):
                dataframeAnalysis = pd.DataFrame([result['analysisData']], index=[analysis])
                dfAnalytics = pd.DataFrame(dataframeAnalysis).copy()
                dfAnalytics = dfAnalytics.drop(columns=[col for col in ["id", "conversation", "date"] if col in dfAnalytics.columns])
                totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)
                totalInsightCol.write(f"🔍 Insights :blue-background[**{len(dfAnalytics.columns)}**]")
                totalColumnCol.write(f"➡️ Columns :blue-background[**{len(dataframeAnalysis.columns)}**]")
                totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
                TotalMessageCol.write(f"💬 Messages :blue-background[**{len(result['conversation'])}**]")
                st.dataframe(dataframeAnalysis)

                for message in result["conversation"]:
                    if message["role"] == "assistant":
                        st.chat_message("assistant").write(message["content"])
                    else:
                        st.chat_message("user").write(message["content"])

    st.toast("Analysis Completed", icon="✅")

Sidebar("Genii • Conversation Analysis | Static Analysis", '🧞 :violet[Genii] • Conversation Analysis', "⚙️ Genii Dataset Static Analysis")
main()
from io import StringIO
import streamlit as st
import pandas as pd
import asyncio

from src.components.sidebar import Sidebar
from src.components.filterDataframe import FilterDataframe
from src.components.analysisSettings import AnalysisSettings

from src.shared.prompts import getStructureJsonPrompt, getReportWithVerbatimPrompt

from src.shared.openaiUtils import sendCompletionToLlm, generateReport
from src.shared.genericUtils import extractStructureTypesFromObject, extractJsonObjectFromText, verifyStructureTable
from src.shared.openaiUtils import generateRerankedConversations
from src.shared.chartUtils import generateBubbleChart
from src.shared.embeddingUtils import getDataframeWithEmbeddings, getPointsForTSNE
from src.shared.conversationsUtils import extractJsonConversationsDataFromTable, conversationsAnalysisTasks


def main():
    uploadedFile = st.file_uploader("Choose a file")

    if uploadedFile is None:
        st.stop()

    uploadedFileData = pd.read_csv(uploadedFile)

    st.write("Dataset Preview:")
    st.write(uploadedFileData)

    if verifyStructureTable(uploadedFileData, ['ID', 'ROLE', 'CONTENT','DATE']):
        jsonConversationsData = extractJsonConversationsDataFromTable(uploadedFileData)
    else:
        st.error("The file structure is incorrect. Please ensure it has 'ID', 'ROLE', 'CONTENT' and 'DATE' columns.")

    insightsToAnalysePrompt, OpenAiApiModelAnalysis, reportPrompt, OpenAiApiModelReport, showReport, showbubbleChart, showIndividualConversationsAnalysis, btnAnalyze, allowToFilterWithChart = AnalysisSettings(uploadedFile is None)

    if btnAnalyze:
        st.divider()
        with st.spinner(f"Sending a request to {OpenAiApiModelAnalysis} to get the structure of the analysis..."):
            try:
                llmResponse= sendCompletionToLlm(getStructureJsonPrompt(insightsToAnalysePrompt), OpenAiApiModelAnalysis, asyncronous=False)
                try:
                    extractedJsonObject = extractJsonObjectFromText(llmResponse)
                    referenceJsonStructureTypes = extractStructureTypesFromObject(extractedJsonObject)
                    st.success(f"Received the structure of the analysis from {OpenAiApiModelAnalysis} successfully", icon='✅')
                except Exception as e:
                    st.error(f"❌ Error Parsing {OpenAiApiModelAnalysis} response in json: {e}")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Error Sending a request to {OpenAiApiModelAnalysis} to get the structure of the analysis: {e}")
                st.stop()
                
        analysisResultsFormated, analysisResults, analysisResultsJson = asyncio.run(conversationsAnalysisTasks(jsonConversationsData, insightsToAnalysePrompt, referenceJsonStructureTypes, OpenAiApiModelAnalysis))

        with st.expander(f'📚 Conversation analysis final report'):

            analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(analysisResultsFormated).T.to_csv(index=False)))

            if showReport:
                generateReport(getReportWithVerbatimPrompt(reportPrompt, analysisResults), OpenAiApiModelReport)

            st.write("📊 Conversations Analysis:")
            with st.spinner('Wait for it...'):
                if allowToFilterWithChart:
                    analysisResultsFormatedForReport = pd.read_csv(StringIO(pd.DataFrame(getDataframeWithEmbeddings(analysisResultsFormatedForReport, 'conversation')).to_csv(index=False)))
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
                    totalInsightCol, totalColumnCol, totalProjectRow, TotalMessageCol= st.columns(4)
                    totalInsightCol.write(f"🔍 Insights :blue-background[**{len(analysisResultsJson)}**]")
                    totalColumnCol.write(f"➡️ Columns :blue-background[**{len(analysisResultsFormatedForReport.columns)}**]")
                    totalProjectRow.write(f"⬇️ Row :blue-background[**1**]")
                    TotalMessageCol.write(f"💬 Messages :blue-background[**{len(result['conversation'])}**]")
                    st.dataframe(result['analysisData'])

                    for message in result["conversation"]:
                        if message["role"] == "assistant":
                            st.chat_message("assistant").write(message["content"])
                        else:
                            st.chat_message("user").write(message["content"])

        st.toast("Analysis Completed", icon="✅")

Sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "📄 Dataset File Analysis")
main()
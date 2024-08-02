from src.shared.openaiUtils import OPENAI_API_MODELS
from src.shared.prompts import INSIGHTS_TEMPLATE_PROMPT, REPORT_TEMPLATE_PROMPT, INITIALS_INSIGHTS_TEMPLATE_PROMPT
import streamlit as st

def AnalysisSettings(disabled=False):
    st.divider()
    with st.expander('🔎 Analysis Prompts'):
        insightsToAnalysePrompt = st.text_area(
                label="Enter a prompt to analyze the conversations:",
                value=INSIGHTS_TEMPLATE_PROMPT,
                height=300,
            )
        OpenAiApiModelAnalysis = st.selectbox(
            "Select a model:",
            [model for model in OPENAI_API_MODELS],
            index=3,
            label_visibility="collapsed",
            key="OpenAiApiModel",
        )

    insightsToAnalysePrompt = f"{INITIALS_INSIGHTS_TEMPLATE_PROMPT}\n{insightsToAnalysePrompt}"

    with st.expander('📖 Report Prompts'):
        reportPrompt = st.text_area(
                label="Enter a prompt to generate a conversations report:",
                value=REPORT_TEMPLATE_PROMPT,
                height=300,
                key="customPromptReport",
            )
        
        OpenAiApiModelReport = st.selectbox(
            "Select a model:",
            [model for model in OPENAI_API_MODELS],
            index=3,
            label_visibility="collapsed",
        )

    with st.expander('⚙️ Advanced Settings'):
        showReport = st.checkbox("show report", value=False)
        allowToFilterWithChart = st.checkbox("allow to filter with chart", value=False)
        showbubbleChart = st.checkbox("show bubble chart", value=False)
        showIndividualConversationsAnalysis = st.checkbox("show individual conversations", value=True)

    btnAnalyze= st.button(
        "Analyze",
        use_container_width=True,
        type="primary",
        disabled=disabled,
    )

    return insightsToAnalysePrompt, OpenAiApiModelAnalysis, reportPrompt, OpenAiApiModelReport, showReport, showbubbleChart, showIndividualConversationsAnalysis, btnAnalyze, allowToFilterWithChart
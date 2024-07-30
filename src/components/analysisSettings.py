from turtle import st
from shared.openaiUtils import OPENAI_API_MODELS
from src.shared.prompts import ANALYSIS_TEMPLATE_PROMPT, REPORT_TEMPLATE_PROMPT


def AnalysisSettings(disabled=False):
    with st.expander('🔎 Analysis Prompts'):
        analysisPrompt = st.text_area(
                label="Enter a prompt to analyze the conversations:",
                value=ANALYSIS_TEMPLATE_PROMPT,
                height=300,
            )
        OpenAiApiModelAnalysis = st.selectbox(
            "Select a model:",
            [model for model in OPENAI_API_MODELS],
            index=3,
            label_visibility="collapsed",
            key="OpenAiApiModel",
        )

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
        showReport = st.checkbox("show report", value=True)
        showbubbleChart = st.checkbox("show bubble chart", value=True)
        showIndividualConversationsAnalysis = st.checkbox("show individual conversations", value=True)

    btnAnalyze= st.button(
        "Analyze",
        use_container_width=True,
        type="primary",
        disabled=disabled,
    )

    return analysisPrompt, OpenAiApiModelAnalysis, reportPrompt, OpenAiApiModelReport, showReport, showbubbleChart, showIndividualConversationsAnalysis, btnAnalyze
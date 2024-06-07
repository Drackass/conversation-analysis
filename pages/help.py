import streamlit as st
from src.components.sidebar import sidebar

sidebar("Genii • Conversation Analysis | Help Center", '🧞 :violet[Genii] • Conversation Analysis', "🛟 Help Center - Conversion Analysis by Tolk.ai")

st.warning('**Warning:** This page is outdated', icon="⚠️")
st.markdown('''## Welcome to the Help Center

Our comprehensive help center is here to assist you in navigating and utilizing our cutting-edge conversion analysis platform. Below, you'll find detailed information about the various features, functionalities, and supported formats to help you make the most of our solution.

### 1. Getting Started
Learn how to set up your account, navigate the platform, and start analyzing your conversations with ease. Our intuitive no-code interface ensures a seamless experience from the get-go.

### 2. Project-Based Conversation Analysis
#### Select a Project by Email
1. **Navigate to the Project Selection Page**: Go to the project selection section on the platform.
2. **Choose Email**: Enter the email associated with the project you want to analyze.
3. **Select Project**: Click on the project from the list displayed.

#### Filter Conversations
1. **Set Conversation Limits**: Use the filter options to limit conversations by criteria such as duration or type of interaction.
2. **Apply Date Range Filter**: Choose the date range for the conversations you want to analyze.

#### Use Custom Prompts
1. **Create Custom Prompts**: Enter specific prompts tailored to your analysis needs.
2. **Save and Apply**: Save the prompts and apply them to guide the analysis.

#### Custom Azure OpenAI Models
1. **Access Model Settings**: Navigate to the model settings section.
2. **Select Custom Model**: Choose and configure a custom Azure OpenAI model that fits your requirements.

#### Fetch and Organize Conversations
1. **Retrieve Conversations**: Click on the fetch button to get conversations according to your filters and project ID.
2. **Display Analysis**: View the organized analysis for each conversation, presented clearly on the dashboard.

#### Extract Custom Insights
1. **Insights Boxes**: Extract crucial insights with custom text boxes.
2. **Metrics**: Identify emotions and sentiment to gauge client satisfaction.
3. **Progress Indicators**: Assess the quality of service provided based on the conversation.

#### View Entire Conversation
1. **Full Conversation Display**: Click on the conversation link to view the entire exchange for a comprehensive analysis.

### 3. Individual Conversation Analysis
- **Direct Analysis**: Analyze a specific conversation by providing its ID directly. Follow the same steps for filtering, using custom prompts, and extracting insights as in project-based analysis.

### 4. Custom Dataset File Analysis
#### Import Custom Datasets
1. **Drag and Drop**: Drag and drop your tabular documents containing conversations into the platform.
2. **Create Custom Conversations**: Alternatively, create your own conversations directly on the platform.

#### Advanced Analysis
- **Apply Analysis Tools**: Use the same advanced analysis tools as in project-based analysis to gain insights from your custom datasets.

### 5. Insights Entities
#### Boxes
Extract crucial insights beyond the surface-level conversation.
- **icon**: (emoji)
- **label**: (string)
- **value**: (string e.g. "Extract crucial insights beyond the surface-level conversation.")
- **type**: ("info"|"success"|"warning"|"error")''')
with st.container(border=True):
    st.info('**Info:** Extract crucial insights beyond the surface-level conversation.', icon="ℹ️")
    st.success('**Success:** This is a success message!', icon="✅")
    st.warning('**Warning:** This is a warning', icon="⚠️")
    st.error('**Error:** This is an error', icon="🚨")

st.markdown('''#### Metrics
Identify emotions and sentiment to gauge client satisfaction.
- **name**: (string)
- **value**: (string e.g. "positive"|"constructive"|"negative"|"neutral")
- **delta**: (average number between -100 and 100)''')

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.container(border=True).metric("Temperature", "70 °F", "1.2 °F")
    col2.container(border=True).metric("Wind", "9 mph", "-8%")
    col3.container(border=True).metric("Humidity", "86%", "4%")

st.markdown('''#### Progress
Assess the quality of service provided based on the conversation.
- **name**: (string)
- **value**: (string e.g. "Very Poor"|"Poor"|"Fair"|"Good"|"Excellent")
- **delta**: (average number between 0 and 100)''')

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    col1.container(border=True).progress(20, "Very Poor")
    col2.container(border=True).progress(40, "Poor")
    col3.container(border=True).progress(60, "Fair")

st.markdown('''### 6. Supported File Formats
- **CSV**: The application supports CSV file formats for uploading conversation datasets. Ensure that your dataset is in CSV format before uploading it to the platform.

| role | message |
| :------------ | :------------ |
| user | dummyUserMessage |
| assistant | dummyAssistantMessage |

---

Our help center is continuously updated to provide you with the latest information and support. If you have any questions or need further assistance, please do not hesitate to reach out to our support team.''')
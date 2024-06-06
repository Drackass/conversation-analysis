import streamlit as st
from src.components.sidebar import sidebar

sidebar("Genii • Conversation Analysis",'🧞 :violet[Genii] • Conversation Analysis', "✨ Introduction")

st.image("public/genii.jpeg")

st.markdown('''## Welcome to Tolk.ai's Conversion Analysis Platform

We are excited to introduce our cutting-edge conversion analysis platform, designed to transform your professional and client interactions into valuable insights. By leveraging the conversational resources extracted from the Genii chatbot, our platform helps you maximize conversion rates and optimize communication strategies with unparalleled precision and ease.

### Why Choose Our Conversion Analysis Platform?

- **Powerful**: Harness the power of a generative AI capable of analyzing a wide range of conversational data sources, including phone calls, emails, support tickets, and virtual agent interactions.
- **Simple**: An intuitive, no-code interface that requires no setup.
- **Scalable**: A robust infrastructure hosted on Microsoft Azure (Europe), ready to grow with your needs.
- **Secure**: Fully compliant with GDPR, ensuring your client data remains secure and compartmentalized.

### Key Features

#### Project-Based Conversation Analysis
- **Project Selection**: Choose a project to analyze by simply selecting an email.
- **Conversation Filtering**: Limit the conversations to be analyzed based on specific criteria (e.g., duration, interaction type).
- **Date Range Filtering**: Analyze conversations within a specific time frame.
- **Custom Prompts**: Use tailored prompts to guide the analysis according to your specific needs.
- **Custom Azure OpenAI Model**: Adapt the AI to your needs with custom models.
- **Conversation Retrieval**: Filter and display conversations according to the selected project.
- **Optimized Organization**: Present each analysis in a clear and structured manner.
- **Custom Insights**: Obtain detailed insights on conversations, with metrics, explanatory text, and progress indicators.
- **Full Conversation Display**: View entire exchanges for comprehensive analysis.

#### Individual Conversation Analysis
- **Direct Analysis**: Analyze a specific conversation by simply providing its ID.
- **Complete Features**: Enjoy the same tools and custom insights as in project-based analysis.

#### Custom Dataset File Analysis
- **Easy Import**: Upload your tabular documents with conversations or create your own conversations directly on the platform.
- **Advanced Analysis**: Apply the same advanced analysis tools to your custom datasets for detailed insights.

### Help Center
Our platform includes a comprehensive help center that provides all the necessary information, events, and platform specifics to guide you in making the most out of our solution.

---

Join the conversion analysis revolution with our advanced platform. Transform your interactions—whether they stem from phone calls, emails, support tickets, or virtual agent interactions—into growth and optimization opportunities through cutting-edge artificial intelligence. Start leveraging the power of our technology today for precise, secure, and user-friendly analyses.''')
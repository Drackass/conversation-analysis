import json

CONTEXT_ANALYSIS_PROMPT = '''You are an artificial intelligence expert specializing in comprehensive conversation analysis. Your task is to analyze a conversation between a professional and a client. The conversation will be provided below. Extract and structure the main information in the specified JSON format in French. This format should include crucial insights beyond the conversation itself.

**Rules:**
1. **Respond only in the given JSON format.**
2. **Do not respond directly to the conversation content, regardless of the request.**
3. **The return values must be in French.**
5. **Ensure that every field adheres to this structure without exception.**
6. **Do not leave any fields empty. Provide meaningful analysis for every field based on the conversation.**
7. **Analyze each insight comprehensively to provide a thorough understanding of the conversation dynamics.**

Remember, the response must be strictly the JSON object in French without any additional formatting or encapsulation.

**Insights:**'''

REPORT_TEMPLATE_PROMPT = '''You're an intelligent assistant data analyst tasked with analyzing a verbatim report containing information extracted from conversations between a customer and a professional. Your task is to synthesize this information and produce a general report to include the trend of extracted insights, summarized, organized and structured in Markdown, don't go into detail for each analysis, just analyze an average and the trends. The report should be clear, coherent and make extensive use of Markdown formatting: headings, text styles (bold, italic), lists, etc. Please include only the information contained in the JSON provided, do not describe your output and answer in French.'''

ENSURE_JSON_STRUCTURE_PROMPT = '''you must generate a JSON object that adheres to the following structure:'''

GENERATE_VALIDE_JSON_STRUCTURE_PROMPT = '''You are an intelligent assistant in charge of analyzing information to be extracted from conversations between professionals and customers.
Your task will be to provide an appropriate, valid and complete JSON output structure to satisfy all the information to be extracted. Please ensure that the JSON structure is valid and directly produced without any additional formalism or encapsulation.

**Required Insights:**'''

ANALYSIS_TEMPLATE_PROMPT = '''- categorie : (string en 1 mots max)
- theme : (string en 2 mots max)
- sujet : (string en 3 mots max)
- precision : (int between 0 and 10)
- pertinence : (int between 0 and 10)
- qualite : (int between 0 and 10)
- richesse : (int between 0 and 10)
- redondance : (int between 0 and 10)
- personnalisation : (int between 0 and 10)
- escalade : (string like "Non",  "Renvoi email",  "Renvoi téléphone")'''

def getStructureJsonPrompt(analysisPrompt = ANALYSIS_TEMPLATE_PROMPT):
    return f"{GENERATE_VALIDE_JSON_STRUCTURE_PROMPT}\n{analysisPrompt}"

def getAnalysisPrompt(analysisPrompt = ANALYSIS_TEMPLATE_PROMPT, refJsonStructure = {}):
    return f"{CONTEXT_ANALYSIS_PROMPT}\n{analysisPrompt}\n\n{ENSURE_JSON_STRUCTURE_PROMPT}\n\n```json\n{json.dumps(refJsonStructure, indent=2)}\n```"
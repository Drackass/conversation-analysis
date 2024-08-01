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

INSIGHTS_TO_TEMPLATE_PROMPT = '''- categorie : (string en 1 mots max)
- theme : (string en 2 mots max)
- sujet : (string en 3 mots max)
- precision : (int between 0 and 10)
- pertinence : (int between 0 and 10)
- qualite : (int between 0 and 10)
- richesse : (int between 0 and 10)
- redondance : (int between 0 and 10)
- personnalisation : (int between 0 and 10)
- escalade : (string like "Non",  "Renvoi email",  "Renvoi téléphone")'''

def getStructureJsonPrompt(analysisPrompt = INSIGHTS_TO_TEMPLATE_PROMPT):
    return f"{GENERATE_VALIDE_JSON_STRUCTURE_PROMPT}\n{analysisPrompt}"

def getAnalysisPrompt(analysisPrompt = INSIGHTS_TO_TEMPLATE_PROMPT, refJsonStructure = {}):
    return f"{CONTEXT_ANALYSIS_PROMPT}\n{analysisPrompt}\n\n{ENSURE_JSON_STRUCTURE_PROMPT}\n\n```json\n{json.dumps(refJsonStructure, indent=2)}\n```"

def getReportWithVerbatimPrompt(reportPrompt = REPORT_TEMPLATE_PROMPT, analysisResults = {}):
    return f"{reportPrompt}\n\n```json\n{json.dumps(analysisResults, indent=2)}\n```"

def getRerankedConversationPrompt(formated_json):
    return '''Réorganise, syntétise et normalise les données suivantes en un arbre de catégories et thèmes généraux puis associe tous les sujets à un ou plusieurs des thèmes généré dans la structure JSON suivante:
    ```json
    {
        "categorie1": {
            "theme1": ["sujet1", "sujet2", "sujet3"],
            "theme2": ["sujet4", "sujet5", "sujet6"],
            "themeX": ["sujet7", "sujet8", "sujet9"],
        },
        "categorie2": {
            "theme1": ["sujet10", "sujet11", "sujet12"],
            "theme2": ["sujet13", "sujet14", "sujet15"],
            "themeX": ["sujet16", "sujet17", "sujet18"],
        },
        "categorieX": {
            "theme1": ["sujet19", "sujet20", "sujet21"],
            "theme2": ["sujet22", "sujet23", "sujet24"],
            "themeX": ["sujet25", "sujet26", "sujet27"],
        },
    }
    ```

    Données à utiliser:
    ```json
    ''' + formated_json + '''
    ```

    assurez-vous que les catégories et les thèmes soient générés de manière à ce qu'ils soient les plus pertinents en en générent le moins que possibles, les quelques thèmes générés doivent êtres assez larges pour anglobé le plus de sujets possible.
    le retour de cette requête devra contenir seulement la structure JSON généré, sans inclure les données d'origine dans la réponse ni toute autre information ou formalisme supplémentaire.'''


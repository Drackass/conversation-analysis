import json
import openai
import pandas as pd
from src.components.sidebar import sidebar
import streamlit as st

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_agraph import agraph, Node, Edge, Config
from src.routes import sendCompletionToLlm

sidebar("Genii • Conversation Analysis | Bubble Chart", '🧞 :violet[Genii] • Conversation Analysis', "📊 Bubble Chart")

def generate_bubble_chart(data):
    nodes = []
    edges = []
    node_counter = 0  # Compteur pour assurer l'unicité des identifiants
    # {'category': '#3a365c', 'theme': '#4b3b8f', 'sub_theme': '##3A365C'}
    # Ajouter le noeud central
    nodes.append(Node(id="Start", label="Start", size=40, color='#363b4f'))
    
    # Parcourir les catégories, thèmes et sujets pour ajouter les noeuds et les arêtes
    for category, themes in data.items():
        category_id = f"category_{node_counter}"
        nodes.append(Node(id=category_id, label=category, size=30, color='#4b3b8f'))
        edges.append(Edge(source="Start", target=category_id))
        node_counter += 1
        
        for theme, subjects in themes.items():
            theme_id = f"theme_{node_counter}"  # Assurer des identifiants uniques
            nodes.append(Node(id=theme_id, label=theme, size=20, color='#816a9e'))
            edges.append(Edge(source=category_id, target=theme_id))
            node_counter += 1
            
            for subject in subjects:
                subject_id = f"subject_{node_counter}"  # Assurer des identifiants uniques
                nodes.append(Node(id=subject_id, label=subject, size=10, color='#e1d0ed'))
                edges.append(Edge(source=theme_id, target=subject_id))
                node_counter += 1
    
    # Configuration du graphique
    config = Config(
        width=1000,
        height=1000,

    )
    
    # Affichage du graphique avec streamlit-agraph
    return_value = agraph(nodes=nodes, edges=edges, config=config)
    return return_value

if st.button("Generate", type="primary"):
    
    
    input_datapath = "data/bubbleDataset.csv"
    df = pd.read_csv(input_datapath)
    # st.dataframe(df)
    
    formatedJson = df.to_json()
    
    prompt = '''Réorganise, syntétise et normalise les données suivantes en un arbre de catégories et thèmes généraux puis associe tous les sujets à un ou plusieurs des thèmes généré dans la structure JSON suivante:
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
    ''' + formatedJson + '''
    ```

    assurez-vous que les catégories et les thèmes soient générés de manière à ce qu'ils soient les plus pertinents en en générent le moins que possibles, les quelques thèmes générés doivent êtres assez larges pour anglobé le plus de sujets possible.
    le retour de cette requête devra contenir seulement la structure JSON généré, sans inclure les données d'origine dans la réponse ni toute autre information ou formalisme supplémentaire.'''
    
    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    llmResponse = sendCompletionToLlm(prompt, "gpt-3.5-turbo", client)
    
    # essayer de convertir la réponse string du llm en json puis de l'afficher
    try:
        llmResponseJson = json.loads(llmResponse)
        # st.json(llmResponseJson)
    except:
        st.write(llmResponse)
        

    # st.title("Graphique de Bulles Hiérarchique")
    generate_bubble_chart(llmResponseJson)
    
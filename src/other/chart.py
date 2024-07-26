# utils.py
import pandas as pd
import numpy as np
from ast import literal_eval
from io import StringIO
from sklearn.manifold import TSNE
import plotly.express as px
from difflib import SequenceMatcher
import json
from streamlit_agraph import agraph, Node, Edge, Config
import tiktoken
from src.other.embeddings_utils import get_embedding
from src.routes import sendCompletionToLlm
import openai
import streamlit as st
from src.utils import extract_json_structure, extract_json_object

def generate_embedding(dataframe, column, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base", top_n=1000):
    data = dataframe.tail(top_n * 2)
    encoding = tiktoken.get_encoding(embedding_encoding)
    data["n_tokens"] = data[column].apply(lambda x: len(encoding.encode(x)))
    data = data[data.n_tokens <= max_tokens].tail(top_n)
    data["embedding"] = data[column].apply(lambda x: get_embedding(x, model=embedding_model))
    return data

def generateEmbedding(dataframe, column, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base", top_n=1000):
    themes = dataframe.tail(top_n * 2)
    encoding = tiktoken.get_encoding(embedding_encoding)
    themes["n_tokens"] = themes[column].apply(lambda x: len(encoding.encode(x)))
    themes = themes[themes.n_tokens <= max_tokens].tail(top_n)
    themes["embedding"] = themes[column].apply(lambda x: get_embedding(x, model=embedding_model))
    
    # Calculate similarity between embeddings
    embeddings = np.array(themes["embedding"].to_list())
    similarity_matrix = np.dot(embeddings, embeddings.T)
    np.fill_diagonal(similarity_matrix, 0)  # Set diagonal elements to 0 to avoid self-similarity
    
    # Remove occurrences with high similarity
    threshold = 0.9  # Set the threshold for similarity
    similar_occurrences = np.where(similarity_matrix > threshold)
    unique_occurrences = np.unique(similar_occurrences[0])
    themes = themes.drop(themes.index[unique_occurrences[1:]]).reset_index(drop=True)
    
    themes["id"] = themes.index + 1
    
    return themes



def filter_similar_embeddings(themes, threshold=0.9):
    embeddings = np.array(themes["embedding"].to_list())
    similarity_matrix = np.dot(embeddings, embeddings.T)
    np.fill_diagonal(similarity_matrix, 0)
    similar_occurrences = np.where(similarity_matrix > threshold)
    unique_occurrences = np.unique(similar_occurrences[0])
    themes = themes.drop(themes.index[unique_occurrences[1:]]).reset_index(drop=True)
    themes["id"] = themes.index + 1
    return themes

def generate_tsne_chart(dataframe, color_column, size_column=None):
    matrix = np.array(dataframe.embedding.apply(literal_eval).to_list())
    n_samples = matrix.shape[0]
    perplexity = min(15, n_samples - 1)
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    dataframe['x'] = vis_dims[:, 0]
    dataframe['y'] = vis_dims[:, 1]
    fig = px.scatter(dataframe, x='x', y='y', color=color_column, size=size_column)
    return fig


def normalize_themes(themes, similarity_threshold=0.8):
    normalized_themes = []
    unique_themes = {}

    for theme in themes:
        normalized_theme = theme.strip().lower()
        found_similar = False
        for unique_theme in unique_themes:
            if SequenceMatcher(None, normalized_theme, unique_theme).ratio() > similarity_threshold:
                normalized_themes.append(unique_themes[unique_theme])
                found_similar = True
                break
        if not found_similar:
            unique_themes[normalized_theme] = theme
            normalized_themes.append(theme)
    return normalized_themes

def generate_bubble_chart(data):
    nodes = []
    edges = []
    node_counter = 0

    nodes.append(Node(id="Start", label="Start", size=40, color='#363b4f'))

    for category, themes in data.items():
        category_id = f"category_{node_counter}"
        nodes.append(Node(id=category_id, label=category, size=30, color='#4b3b8f'))
        edges.append(Edge(source="Start", target=category_id))
        node_counter += 1

        for theme, subjects in themes.items():
            theme_id = f"theme_{node_counter}"
            nodes.append(Node(id=theme_id, label=theme, size=20, color='#816a9e'))
            edges.append(Edge(source=category_id, target=theme_id))
            node_counter += 1

            for subject in subjects:
                subject_id = f"subject_{node_counter}"
                nodes.append(Node(id=subject_id, label=subject, size=10, color='#e1d0ed'))
                edges.append(Edge(source=theme_id, target=subject_id))
                node_counter += 1

    config = Config(
        width=1000,
        height=1000,
    )
    return agraph(nodes=nodes, edges=edges, config=config)

def generate_bubble_chart_from_prompt(df, api_key):
    # extract categorie, theme and subject columns
    df = df[["categorie", "theme", "sujet"]]
    formated_json = df.to_json()
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
    ''' + formated_json + '''
    ```

    assurez-vous que les catégories et les thèmes soient générés de manière à ce qu'ils soient les plus pertinents en en générent le moins que possibles, les quelques thèmes générés doivent êtres assez larges pour anglobé le plus de sujets possible.
    le retour de cette requête devra contenir seulement la structure JSON généré, sans inclure les données d'origine dans la réponse ni toute autre information ou formalisme supplémentaire.'''

    client = openai.OpenAI(api_key=api_key)
    llm_response = sendCompletionToLlm(prompt, "gpt-4-turbo", client)

    return extract_json_object(llm_response)

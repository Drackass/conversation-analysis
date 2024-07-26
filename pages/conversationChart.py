import pandas as pd
from src.components.sidebar import sidebar
import streamlit as st
import tiktoken
from src.other.embeddings_utils import get_embedding
import numpy as np
from sklearn.manifold import TSNE
from ast import literal_eval
from io import StringIO
import plotly.express as px
from difflib import SequenceMatcher

sidebar("Genii • Conversation Analysis | Conversation Chart", '🧞 :violet[Genii] • Conversation Analysis', "📊 Conversation Chart")

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

def generateEmbedding(dataframe, column, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base", top_n=1000):
    convos = dataframe.tail(top_n * 2)
    encoding = tiktoken.get_encoding(embedding_encoding)
    convos["n_tokens"] = convos[column].apply(lambda x: len(encoding.encode(x)))
    convos = convos[convos.n_tokens <= max_tokens].tail(top_n)
    convos["embedding"] = convos[column].apply(lambda x: get_embedding(x, model=embedding_model))
    return convos

@st.experimental_fragment
def generateChart(dfWithEmbedding):
    dataframe = pd.read_csv(StringIO(dfWithEmbedding.to_csv(index=False)))
    matrix = np.array(dataframe.embedding.apply(literal_eval).to_list())
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    dataframe['x'] = vis_dims[:, 0]
    dataframe['y'] = vis_dims[:, 1]
    fig = px.scatter(dataframe, x='x', y='y', color='theme')
    st.plotly_chart(fig, on_select="rerun", key="my_chart")

if st.button("Generate", type="primary"):
    input_datapath = "data/themeDataset.csv"
    baseData = pd.read_csv(input_datapath, index_col=0)
    
    # Normalize the 'theme' column
    baseData['theme'] = normalize_themes(baseData['theme'])
    
    # st.write("Dataset Preview:")
    # st.dataframe(baseData)
    dfWithEmbedding = generateEmbedding(baseData, "conversation")
    # st.dataframe(dfWithEmbedding)
    generateChart(dfWithEmbedding)

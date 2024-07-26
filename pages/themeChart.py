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

sidebar("Genii • Conversation Analysis | Theme Chart", '🧞 :violet[Genii] • Conversation Analysis', "📊 Theme Chart")

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

@st.experimental_fragment
def generateChart(dfWithEmbedding):
    dataframe = pd.read_csv(StringIO(dfWithEmbedding.to_csv(index=False)))
    matrix = np.array(dataframe.embedding.apply(literal_eval).to_list())
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    dataframe['x'] = vis_dims[:, 0]
    dataframe['y'] = vis_dims[:, 1]
    fig = px.scatter(dataframe, x='x', y='y', color='theme', hover_data=['id'], size='count')
    event_data = st.plotly_chart(fig, on_select="rerun", key="my_chart" )
    # st.json(event_data)

if st.button("Generate", type="primary"):

    col1, col2 = st.columns([3, 1])

    with col1:
        input_datapath = "data/themeDataset.csv"
        baseData = pd.read_csv(input_datapath, index_col=0)
        # st.write("Dataset Preview:")
        # st.dataframe(baseData)
        
    with col2:
        dfThemes = baseData["theme"].str.lower().str.strip().value_counts().reset_index()
        dfThemes.columns = ["theme", "count"]
        # st.write("Themes:")
        # st.dataframe(dfThemes)

    dfWithEmbedding = generateEmbedding(dfThemes, "theme")
    # st.dataframe(dfWithEmbedding)
    
    generateChart(dfWithEmbedding)
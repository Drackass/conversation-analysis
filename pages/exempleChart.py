import streamlit as st
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from ast import literal_eval
import plotly.express as px

from src.components.sidebar import sidebar

# Configuration de la sidebar
sidebar("Genii • Conversation Analysis | Exemple Chart", '🧞 :violet[Genii] • Conversation Analysis', "📊 Exemple Chart")

# Charger les données
datafile_path = "data/fine_food_reviews_with_embeddings_1k.csv"
df = pd.read_csv(datafile_path)

# Convertir les embeddings en liste de listes de floats
matrix = np.array(df.embedding.apply(literal_eval).to_list())

# Créer et transformer les données avec un modèle t-SNE
tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
vis_dims = tsne.fit_transform(matrix)

# Ajouter les dimensions t-SNE et les couleurs au dataframe
df['x'] = vis_dims[:, 0]
df['y'] = vis_dims[:, 1]
colors = ["5", "4", "3", "2", "1"]
colormap = {i+1: color for i, color in enumerate(colors)}
df['color'] = df['Score'].map(colormap)

# Créer le graphique avec Plotly
fig = px.scatter(df, x='x', y='y', color='color', hover_data=['Score', 'Id'])

# Afficher le graphique et activer la sélection avec l'id de l'élément select
event_data = st.plotly_chart(fig, on_select="rerun", key="my_chart" )

# Vérifier et afficher les données sélectionnées
if event_data:
    selected_points = event_data.get('points', [])
    selected_ids = [df.iloc[point['point_index']]['Id'] for point in selected_points]
    st.write("Selected points data:", selected_points)
    st.write("Selected points IDs:", selected_ids)

# Calculer et afficher les centres moyens pour chaque score
for score in [1, 2, 3, 4, 5]:
    avg_x = df[df.Score == score]['x'].mean()
    avg_y = df[df.Score == score]['y'].mean()
    st.text(f'Score {score}: Average x = {avg_x:.2f}, Average y = {avg_y:.2f}')

st.json(event_data)

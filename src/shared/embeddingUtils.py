import pandas as pd
from io import StringIO
import tiktoken
from src.shared.openaiUtils import get_embedding
import numpy as np
from ast import literal_eval
from sklearn.manifold import TSNE

def generateEmbedding(dataframe, column, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base", top_n=1000):
    data = dataframe.tail(top_n * 2)
    encoding = tiktoken.get_encoding(embedding_encoding)
    data["n_tokens"] = data[column].apply(lambda x: len(encoding.encode(x)))
    data = data[data.n_tokens <= max_tokens].tail(top_n)
    data["embedding"] = data[column].apply(lambda x: get_embedding(x, model=embedding_model))
    return data

def getDataframeWithEmbeddings(df, column):
    df_with_embedding = generateEmbedding(df, column)
    csv_data = df_with_embedding.to_csv(index=False)
    df_with_embedding = pd.read_csv(StringIO(csv_data))
    return df_with_embedding

def getPointsForTSNE(df):
    matrix = np.array(df.embedding.apply(literal_eval).to_list())
    n_samples = matrix.shape[0]
    perplexity = min(15, n_samples - 1)
    tsne = TSNE(n_components=2, perplexity=max(0.1, float(perplexity)), random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    df['x'] = vis_dims[:, 0]
    df['y'] = vis_dims[:, 1]
    return df

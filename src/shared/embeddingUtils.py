import asyncio
import threading
import pandas as pd
from io import StringIO
import tiktoken
from src.shared.openaiUtils import get_embedding
import numpy as np
from ast import literal_eval
from sklearn.manifold import TSNE
import streamlit as st

def generateEmbedding(dataframe, column, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base", top_n=1000):
    data = dataframe.tail(top_n * 2)
    encoding = tiktoken.get_encoding(embedding_encoding)
    data["n_tokens"] = data[column].apply(lambda x: len(encoding.encode(str(x))))
    data = data[data.n_tokens <= max_tokens].tail(top_n)
    data["embedding"] = data[column].apply(lambda x: get_embedding(str(x), model=embedding_model))
    return data

def getDataframeWithEmbeddings(df, column):
    df_with_embedding = generateEmbedding(df, column)
    csv_data = df_with_embedding.to_csv(index=False)
    df_with_embedding = pd.read_csv(StringIO(csv_data))
    return df_with_embedding

async def generate_embedding_for_row(index, row, column, progress, total_rows, lock, progress_bar, dataframeWithEmbeddingsresult, embedding_model="text-embedding-3-small", max_tokens=8000, embedding_encoding="cl100k_base"):
    row[column] = str(row[column])
    # st.write(row[column])
    encoding = tiktoken.get_encoding(embedding_encoding)
    row["n_tokens"] = len(encoding.encode(row[column]))
    if row["n_tokens"] <= max_tokens:
        row["embedding"] = await get_embedding(row[column], model=embedding_model)
    else:
        row["embedding"] = None
    dataframeWithEmbeddingsresult.loc[index] = row

    with lock:
        progress[0] += 1
        progress_bar.progress(progress[0] / total_rows, text=f"Analyzing Conversation {progress[0]}/{total_rows}")

async def getDataframeWithEmbeddingsTask(dataframe, columnToEmbed):
    progress_bar = st.progress(0, text="Adding Embeddings...")
    total_rows = len(dataframe)
    progress = [0]
    tasks = []
    dataframeWithEmbeddingsresult = dataframe.copy()
    dataframeWithEmbeddingsresult["embedding"] = None
    dataframeWithEmbeddingsresult["n_tokens"] = None
    lock = threading.Lock()
    
    for index, row in dataframe.iterrows():
        task = generate_embedding_for_row(index, row, columnToEmbed, progress, total_rows, lock, progress_bar, dataframeWithEmbeddingsresult)
        tasks.append(task)
    await asyncio.gather(*tasks)
    st.success(f"{total_rows} Embedding generated", icon='✅')
    progress_bar.empty()
    return dataframeWithEmbeddingsresult

# async def getDataframeWithEmbeddingsTask(analysisResultsFormatedForReport, columnToEmbed):
#     progress_bar = st.progress(0, text="Analyzing Conversations...")
#     total_tuple = len(analysisResultsFormatedForReport)
#     progress = [0]
#     tasks = []
#     dataframeWithEmbeddingsresult = analysisResultsFormatedForReport
#     lock = threading.Lock()
    
#     # for conversation type code exemple to adapte for generrating embeding for each conversation tupple in the dataframe
#     # for conversation in jsonConversationsData:
#     #     task = conversationAnalysis(conversation, progress, total_conversations, lock, progress_bar, insightsToAnalysePrompt, referenceJsonStructureTypes, OpenAiApiModelAnalysis, analysisResultsFormated, analysisResults, analysisResultsJson)
#     #     tasks.append(task)

#     for index, row in analysisResultsFormatedForReport.iterrows():
#         task = getDataframeWithEmbeddings(row, columnToEmbed)
#         # task = asyncio.create_task(getDataframeWithEmbeddings(row, columnToEmbed))
#         tasks.append(task)
#     await asyncio.gather(*tasks)
#     st.success(f"{total_tuple} Embeding generated", icon='✅')
#     progress_bar.empty()
#     return dataframeWithEmbeddingsresult

def getPointsForTSNE(df):
    matrix = np.array(df.embedding.apply(literal_eval).to_list())
    n_samples = matrix.shape[0]
    perplexity = min(15, n_samples - 1)
    tsne = TSNE(n_components=2, perplexity=max(0.1, float(perplexity)), random_state=42, init='random', learning_rate=200)
    vis_dims = tsne.fit_transform(matrix)
    df['x'] = vis_dims[:, 0]
    df['y'] = vis_dims[:, 1]
    return df
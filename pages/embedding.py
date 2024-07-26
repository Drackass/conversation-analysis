from src.components.sidebar import sidebar
import pandas as pd
import tiktoken
import streamlit as st
from src.other.embeddings_utils import get_embedding

sidebar("Genii • Conversation Analysis | Embeding", '🧞 :violet[Genii] • Conversation Analysis', "📄 Embeding")

embedding_model = "text-embedding-3-small"
max_tokens = 8000  # the maximum for text-embedding-3-small is 8191
embedding_encoding = "cl100k_base"

# load & inspect dataset
input_datapath = "data/Reviews100.csv"  # to save space, we provide a pre-filtered dataset
df = pd.read_csv(input_datapath, index_col=0)
df = df[["Time", "ProductId", "UserId", "Score", "Summary", "Text"]]
df = df.dropna()
df["combined"] = (
    "Title: " + df.Summary.str.strip() + "; Content: " + df.Text.str.strip()
)
# df.head(2)
st.write("Dataset Preview:")
st.dataframe(df.head(2))
# subsample to 1k most recent reviews and remove samples that are too long
top_n = 1000
df = df.sort_values("Time").tail(top_n * 2)  # first cut to first 2k entries, assuming less than half will be filtered out
df.drop("Time", axis=1, inplace=True)
encoding = tiktoken.get_encoding(embedding_encoding)
# omit reviews that are too long to embed
df["n_tokens"] = df.combined.apply(lambda x: len(encoding.encode(x)))
df = df[df.n_tokens <= max_tokens].tail(top_n)
st.write(f"Number of reviews after filtering: {len(df)}")
# Ensure you have your API key set in your environment per the README: https://github.com/openai/openai-python#usage
# This may take a few minutes
df["embedding"] = df.combined.apply(lambda x: get_embedding(x, model=embedding_model))
df.to_csv("data/results.csv")
a = get_embedding("hi", model=embedding_model)
st.write(a)
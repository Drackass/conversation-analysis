import re
import json
import streamlit as st
from pandas.api.types import (
    CategoricalDtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd

import pandas as pd
import tiktoken
import streamlit as st

from src.other.embeddings_utils import get_embedding

def describe_content(value, indent=0):
    indent_str = '  ' * indent 
    if isinstance(value, str):
        return f"{indent_str}{value}"
    elif isinstance(value, list):
        return ', '.join(f"{indent_str}- {describe_content(item, indent + 1)}" for item in value)
    elif isinstance(value, dict):
        return '\n'.join(f"{indent_str}{key}:\n{describe_content(val, indent + 1)}" for key, val in value.items())
    else:
        return f"{indent_str}{str(value)}"
    
def format_date_range(conversationDateRange):
    from_date = conversationDateRange["from"].split("T")[0]
    to_date = conversationDateRange["to"].split("T")[0]
    return f"{from_date} - {to_date}"

def details_to_string(details):
    try:
        return f"{details['short_value']}: \n{details['longer_value']} \n({details['justification']}) \n<{details['score']}>"
    except KeyError:
        return describe_content(details)
    
def extract_json_object(response):
    json_object = re.search(r"\{.*\}", response, re.DOTALL)
    if json_object is not None:
        return json.loads(json_object.group(0))
    else:
        return None

def getMetrics(json):
    metrics = {}
    for key, value in json.items():
        if isinstance(value, dict) and "name" in value and "value" in value and "delta" in value:
            metrics[key] = value
    return metrics

def getBoxes(json):
    boxes = {}
    for key, value in json.items():
        if isinstance(value, dict) and "icon" in value and "label" in value and "value" in value and "type" in value:
            boxes[key] = value
    return boxes

def getProgress(json):
    progress = {}
    for key, value in json.items():
        if isinstance(value, dict) and "name" in value and "value" in value and not "delta" in value:
            progress[key] = value
    return progress

def flatten_json(nested_json: dict, exclude: list=[''], sep: str='-') -> dict:
    """
    Flatten a list of nested dicts.
    """
    out = dict()
    def flatten(x: (list, dict, str), name: str='', exclude=exclude):
        if type(x) is dict:
            for a in x:
                if a not in exclude:
                    flatten(x[a], f'{name}{a}{sep}')
        # elif type(x) is list:
        #     i = 0
        #     for a in x:
        #         flatten(a, f'{name}{i}{sep}')
        #         i += 1
        elif type(x) is list:
            out[name[:-1]] = "- " + "\n- ".join(str(item) for item in x)
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out


def extract_json_structure(data):
    if isinstance(data, dict):
        return {key: extract_json_structure(value) for key, value in data.items()}
    elif isinstance(data, list):
        if len(data) > 0:
            return [extract_json_structure(data[0])]
        else:
            return []
    else:
        return type(data).__name__
    


def formalize_messages(json_input):
    formatted_output = []
    for entry in json_input:
        if entry['role'] == 'user':
            formatted_output.append(f"User:\n{entry['content']}\n\n")
        elif entry['role'] == 'assistant':
            formatted_output.append(f"Assistant:\n{entry['content']}\n\n")
    
    return ''.join(formatted_output)


@st.experimental_fragment
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", key="modify_checkbox")

    if not modify:
        rowCol, colCol = st.columns(2)
        rowCol.write(f"➡️ Rows :blue-background[**{len(df)}**]")
        colCol.write(f"➡️ Columns :blue-background[**{len(df.columns)}**]")
        st.dataframe(df)
    else:

        df = df.copy()

        try:
            for col in df.columns:
                if is_object_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass

                if is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.tz_localize(None)

            modification_container = st.container()

            with modification_container:
                to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
                for column in to_filter_columns:
                    left, right = st.columns((1, 20))
                    left.write("↳")
                    if is_numeric_dtype(df[column]) and float(df[column].min()) != float(df[column].max()):
                        _min = float(df[column].min())
                        _max = float(df[column].max())
                        step = (_max - _min) / 100
                        user_num_input = right.slider(
                            f"Values for {column}",
                            min_value=_min,
                            max_value=_max,
                            value=(_min, _max),
                            step=step,
                        )
                        df = df[df[column].between(*user_num_input)]
                    elif is_datetime64_any_dtype(df[column]):
                        user_date_input = right.date_input(
                            f"Values for {column}",
                            value=(
                                df[column].min(),
                                df[column].max(),
                            ),
                        )
                        if len(user_date_input) == 2:
                            user_date_input = tuple(map(pd.to_datetime, user_date_input))
                            start_date, end_date = user_date_input
                            df = df.loc[df[column].between(start_date, end_date)]
                    elif (is_numeric_dtype(df[column])  and float(df[column].min()) == float(df[column].max())) or CategoricalDtype(df[column].fillna("None").unique()):
                        df[column] = df[column].fillna("None")
                        user_cat_input = right.multiselect(
                            f"Values for {column}",
                            df[column].unique(),
                            default=list(df[column].unique()),
                        )
                        df = df[df[column].isin(user_cat_input)]

                    else:
                        user_text_input = right.text_input(
                            f"Substring or regex in {column}",
                        )
                        if user_text_input:
                            df = df[df[column].astype(str).str.contains(user_text_input)]

            rowCol, colCol = st.columns(2)
            rowCol.write(f"➡️ Rows :blue-background[**{len(df)}**]")
            colCol.write(f"➡️ Columns :blue-background[**{len(df.columns)}**]")
            st.dataframe(df)

        except KeyError:
            rowCol, colCol = st.columns(2)
            rowCol.write(f"➡️ Rows :blue-background[**{len(df)}**]")
            colCol.write(f"➡️ Columns :blue-background[**{len(df.columns)}**]")
            st.dataframe(df[df.columns[df.isnull().any()]])

                

def generate_embeddings():
    embedding_model = "text-embedding-3-small"
    embedding_encoding = "cl100k_base"
    max_tokens = 8000  # the maximum for text-embedding-3-small is 8191

    # load & inspect dataset
    input_datapath = "Reviews.csv"  # to save space, we provide a pre-filtered dataset
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
    df.to_csv("data/fine_food_reviews_with_embeddings_1k.csv")

    a = get_embedding("hi", model=embedding_model)

    st.write(a)

    def extraire_json(chaine):
        # Utiliser une expression régulière pour trouver le JSON dans la chaîne
        # Cette expression cherche des chaînes qui ressemblent à des objets JSON
        pattern = re.compile(r'(\{.*?\})', re.DOTALL)
        match = pattern.search(chaine)

        if match:
            json_str = match.group(1)
            try:
                # Charger le JSON extrait
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Erreur de décodage JSON: {e}")
        else:
            raise ValueError("Aucun JSON valide trouvé dans la chaîne.")
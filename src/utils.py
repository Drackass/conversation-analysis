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
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, f'{name}{i}{sep}')
                i += 1
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
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
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
            # Treat columns with < 10 unique values as categorical
            # if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
            if is_numeric_dtype(df[column]):
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
            elif CategoricalDtype(df[column].fillna("None")):
                df[column] = df[column].fillna("None")
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
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
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df
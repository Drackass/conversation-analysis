from io import StringIO
import json
import pandas as pd
import streamlit as st
from src.components.sidebar import sidebar
from src.utils import filter_dataframe, flatten_json
from src.misc import jsonFilterTest
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import numpy as np

# Initialisation de la barre latérale
sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "🔎 Filter Test")

# uploaded_file = st.file_uploader("Choose a file", type=['json'])

# if uploaded_file is not None:
#     jsondata = json.load(uploaded_file)
        

# Utilisation des variables de session pour stocker l'état du bouton
# if 'btn_renderer_clicked' not in st.session_state:
#     st.session_state['btn_renderer_clicked'] = False

# if 'json_analysis' not in st.session_state:
#     st.session_state['json_analysis'] = {
#         "0":{
#             "hello": "world",
#         }
#     }

# jsondata = st.session_state['json_analysis']

# Bouton pour rendre le DataFrame
# btnRenderer = st.button(
#     "Render Dataframe",
#     use_container_width=True,
#     type="primary",
#     disabled=uploaded_file is None,
# )

# if btnRenderer:
#     st.session_state['btn_renderer_clicked'] = True

# if st.session_state['btn_renderer_clicked']:
#     # jsondata = json.loads(jsonFilterTest)

#     result = {}
#     for key, value in jsondata.items():
#         result[key] = flatten_json(value)

#     flatteredJson = result
#     csvformatedjson = pd.DataFrame(flatteredJson).T.to_csv(index=False)
#     df = pd.read_csv(StringIO(csvformatedjson))

#     st.dataframe(filter_dataframe(df))
    

# result = {}
# for key, value in jsondata.items():
#     result[key] = flatten_json(value)
# flatteredJson = result
# csvformatedjson = pd.DataFrame(flatteredJson).T.to_csv(index=False)
# df = pd.read_csv(StringIO(csvformatedjson))
# st.dataframe(filter_dataframe(df))

jsonData = {
    "0": {
        "name": "John",
        "age": 30,
        "city": "New York",
        "date": np.datetime64("2022-01-01")
    },
    "1": {
        "name": "Peter",
        "age": 45,
        "city": "Paris",
        "date": np.datetime64("2022-04-01")
    },
    "2": {
        "name": "Mary",
        "age": 25,
        "city": "London",
        "date": np.datetime64("2022-07-01")
    }
}

csvformatedjson = pd.DataFrame(jsonData).T.to_csv(index=False)
df = pd.read_csv(StringIO(csvformatedjson))
filter_dataframe(df)

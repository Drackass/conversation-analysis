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

# Initialisation de la barre latérale
sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "🔎 Filter Test")

# Text area pour entrer un JSON
# jsonTextArea = st.text_area(
#     label="Enter a json to filter:",
#     value=jsonFilterTest,
#     height=300,
# )

uploaded_file = st.file_uploader("Choose a file", type=['json'])

if uploaded_file is not None:
    jsondata = json.load(uploaded_file)
        

# Utilisation des variables de session pour stocker l'état du bouton
if 'btn_renderer_clicked' not in st.session_state:
    st.session_state['btn_renderer_clicked'] = False

# Bouton pour rendre le DataFrame
btnRenderer = st.button(
    "Render Dataframe",
    use_container_width=True,
    type="primary",
    disabled=uploaded_file is None,
)

if btnRenderer:
    st.session_state['btn_renderer_clicked'] = True

if st.session_state['btn_renderer_clicked']:
    # jsondata = json.loads(jsonFilterTest)

    result = {}
    for key, value in jsondata.items():
        result[key] = flatten_json(value)

    flatteredJson = result
    csvformatedjson = pd.DataFrame(flatteredJson).T.to_csv(index=False)
    df = pd.read_csv(StringIO(csvformatedjson))

    st.dataframe(filter_dataframe(df))
    
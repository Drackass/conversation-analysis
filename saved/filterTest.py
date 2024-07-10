from io import StringIO
import json
import pandas as pd
from src.components.sidebar import sidebar

import streamlit as st

from src.utils import filter_dataframe, flatten_json
from src.misc import jsonFilterTest



sidebar("Genii • Conversation Analysis | DatasetFile", '🧞 :violet[Genii] • Conversation Analysis', "🔎 Filter Test")

# uploaded_file = st.file_uploader("Choose a file")

# if uploaded_file is not None:
#     df = pd.read_csv(uploaded_file)
#     st.write("Dataset Preview:")
#     st.dataframe(filter_dataframe(df))



# jsonTextArea = st.text_area(
#     label="Enter a json to filter:",
#     value=jsonFilterTest,
#     height=300,
# )

# btnRenderer = st.button(
#     "Render Dataframe",
#     use_container_width=True,
#     type="primary",
# )

# if btnRenderer:
#     # st.json(json.loads(jsonFilterTest))
#     jsonBase = json.loads(jsonTextArea)

#     result = {}
#     for key, value in jsonBase.items():
#         # st.write(f"key: {key}")
#         # st.write(f"value: {value}")
#         # st.write(f"flattened value: {flatten_json(value)}")
#         result[key] = flatten_json(value)

#     # st.json(result)

#     # convert to dataframe
#     df = pd.DataFrame.from_dict(result, orient='index')
#     st.dataframe(filter_dataframe(df))


# ---

# loadedJson = json.loads(jsonFilterTest)
# loadedJson = {
#     "name": "John",
#     "age": 30,
#     "cars": {
#         "car1": "Ford",
#         "car2": "BMW",
#         "car3": "Fiat"
#     }
# }


# result = {}
# for key, value in loadedJson.items():
#     # st.write(f"key: {key}")
#     # st.write(f"value: {value}")
#     # st.write(f"flattened value: {flatten_json(value)}")
#     result[key] = flatten_json(value)

# df = pd.DataFrame.from_dict(result, orient='index')

# st.dataframe(filter_dataframe(df))

# st.json(result)

# data_url = "https://raw.githubusercontent.com/mcnakhaee/palmerpenguins/master/palmerpenguins/data/penguins.csv"

# csv = pd.read_csv(data_url)

# # convert csv to json
# loadedJson = csv.to_json(orient="index")

# st.json(loadedJson)


# df = pd.read_csv(data_url)
# st.dataframe(filter_dataframe(df))



# result = flatten_json(loadedJson)

# df = pd.DataFrame.from_dict(result, orient='index').T

# st.dataframe(filter_dataframe(df))

# st.json(result)



# st.dataframe(filter_dataframe(df))

# st.write(data_url)

# data_url = "https://raw.githubusercontent.com/mcnakhaee/palmerpenguins/master/palmerpenguins/data/penguins.csv"

# df = pd.read_csv(data_url)

# # convert csv to json
# loadedJson = df.to_json(orient="index")
# st.json(loadedJson)


# ----------------------------


# converti le json en format csv
# csv = pd.DataFrame(data).T.to_csv(index=False)

# # affiche le csv

# df = pd.read_csv(StringIO(csv))

# st.dataframe(filter_dataframe(df))


# df = pd.DataFrame(data).T
# st.dataframe(filter_dataframe(df))

# ----------------------------

jsonTextArea = st.text_area(
    label="Enter a json to filter:",
    value=jsonFilterTest,
    height=300,
)

btnRenderer = st.button(
    "Render Dataframe",
    use_container_width=True,
    type="primary",
)

if btnRenderer:
    jsondata = json.loads(jsonFilterTest)
    # st.json(jsondata)

    result = {}
    for key, value in jsondata.items():
        result[key] = flatten_json(value)

    flatteredJson = result

    csvformatedjson = pd.DataFrame(flatteredJson).T.to_csv(index=False)

    df = pd.read_csv(StringIO(csvformatedjson))

    st.dataframe(filter_dataframe(df))
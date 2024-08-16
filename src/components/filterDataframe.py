from pandas.api.types import (
    CategoricalDtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import streamlit as st
import plotly.express as px

@st.experimental_fragment
def FilterDataframe(df: pd.DataFrame, allowToFilterWithChart=False) -> pd.DataFrame:
    modify = st.checkbox("Add filters", key="modify_checkbox_chart", value=True)

    colomns = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns]).columns

    if not modify:
        rowCol, colCol = st.columns(2)
        dfToShow = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns])
        dfToShow["date"] = pd.to_datetime(dfToShow["date"]).dt.strftime("%d/%m/%Y")
        rowCol.write(f"➡️ Rows :blue-background[**{len(dfToShow)}**]")
        colCol.write(f"➡️ Columns :blue-background[**{len(dfToShow.columns)}**]")
        st.dataframe(dfToShow)
    else:
        df = df.copy()
        try:
            for col in colomns:
                if is_object_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass
                if is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.tz_localize(None)

            modification_container = st.container()
            with modification_container:
                to_filter_columns = st.multiselect("Filter dataframe on", df.columns, key="to_filter_by_columns")
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

            if allowToFilterWithChart:
                if len(df) < 2:
                    st.info('minimum 2 rows required to plot the chart')
                    dfToShow = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns])
                    dfToShow["date"] = pd.to_datetime(dfToShow["date"]).dt.strftime("%d/%m/%Y")
                    rowCol.write(f"➡️ Rows :blue-background[**{len(dfToShow)}**]")
                    colCol.write(f"➡️ Columns :blue-background[**{len(dfToShow.columns)}**]")
                    st.dataframe(dfToShow)
                else:
                    df = df.copy()
                    dfToShow = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns])
                    dfToShow["date"] = pd.to_datetime(dfToShow["date"]).dt.strftime("%d/%m/%Y")
                    dfFilterColumns = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y", "conversation", "date", "id"] if col in df.columns]).columns
                    dfFilterColumns = [col.lower() for col in dfFilterColumns]
                    dfFilterColumns = list(set(dfFilterColumns))
                    dfFilterColumns.sort()
                    dfFilterColumns = [col for col in dfFilterColumns if col not in ["conversation", "date", "id"]]
                    color_column = st.selectbox("Select the column to use for coloring the chart", dfFilterColumns, key="to_filter_by_chart")
                    with st.spinner('Wait for it...'):
                        fig = px.scatter(df, x='x', y='y', color=color_column, size=None, hover_data=[ 'id', 'sujet'])
                        selectedData = st.plotly_chart(fig, on_select="rerun", key="my_chart_5")
                    
                    ids = [point["customdata"][0] for point in selectedData["selection"]["points"]]
                    if ids:
                        dfToShow = dfToShow[dfToShow["id"].isin(ids)]
                    
                    rowCol, colCol = st.columns(2)
                    rowCol.write(f"➡️ Rows :blue-background[**{len(dfToShow)}**]")
                    colCol.write(f"➡️ Columns :blue-background[**{len(dfToShow.columns)}**]")
                    st.dataframe(dfToShow)

            else:
                dfToShow = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns])
                dfToShow["date"] = pd.to_datetime(dfToShow["date"]).dt.strftime("%d/%m/%Y")
                st.dataframe(dfToShow)

        except KeyError:
            rowCol, colCol = st.columns(2)
            dfToShow = df.drop(columns=[col for col in ["embedding", "n_tokens", "x", "y"] if col in df.columns])
            dfToShow["date"] = pd.to_datetime(dfToShow["date"]).dt.strftime("%d/%m/%Y")
            rowCol.write(f"➡️ Rows :blue-background[**{len(dfToShow)}**]")
            colCol.write(f"➡️ Columns :blue-background[**{len(dfToShow.columns)}**]")
            st.dataframe(dfToShow[dfToShow.columns[dfToShow.isnull().any()]])
import streamlit as st
import datetime
from src.routes import getAllUsers

def projectConversationsTab():
    st.header("Project Conversations Analysis")

    allUsers = getAllUsers()

    allUsers = [{"name": user["name"], "id": user["id"]} for user in allUsers["projects"]]
    
    projectId = st.selectbox("select a user", allUsers, format_func=lambda x: x["name"], index=297, key="projectIdConversations")["id"]

    # find and write the index for the selected user
    # index = next((index for (index, d) in enumerate(allUsers) if d["id"] == projectId), None)
    # st.write(index)

    # projectId = st.text_input("Enter a projectId:", "e51255e3-2790-4ab7-964c-6f898f7e00f7")

    filters = st.multiselect(
    "Filters",
    ["Conversation Limit", "Date Range"],
    ["Conversation Limit", "Date Range"],
    )

    params = {}
    conversationLimit = None
    if "Conversation Limit" in filters:
        with st.container(border=True):
                conversationLimit = st.select_slider(
                "Select a conversations limit",
                options= range(1, 21),
                value=5,
            ),
        params['limit'] = conversationLimit[0]


    conversationDateRange = None
    if "Date Range" in filters:
        with st.container(border=True):
            conversationDateRange = st.date_input("Select a range", (datetime.datetime.now() - datetime.timedelta(days=10), datetime.datetime.now()))
        params['range'] = '{"conditions":[{"operator":"gte","value":"' + conversationDateRange[0].isoformat() + '"},{"operator":"lte","value":"' + conversationDateRange[1].isoformat() + '"}],"field":"date"}'
        params['sort'] = '[{"field":"date","sort":"desc"}]'
        params['offset'] = 0
    else:
        params['range'] = '{{"conditions":[{{"operator":"gte","value":"{}"}},{{"operator":"lte","value":"{}"}}],"field":"date"}}'.format((datetime.datetime.now() - datetime.timedelta(days=3650)).isoformat(), datetime.datetime.now().isoformat())
        params['sort'] = '[{"field":"date","sort":"desc"}]'
        params['offset'] = 0

    return projectId, filters, params, conversationLimit, conversationDateRange

    

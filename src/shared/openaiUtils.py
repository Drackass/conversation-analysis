import openai
import streamlit as st
from src.shared.prompts import getRerankedConversationPrompt
from src.shared.genericUtils import extractJsonObjectFromText
from typing import List

ASYNCRONOUS_CLIENT = openai.AsyncOpenAI(api_key=st.secrets["OPENAI_API_KEY"])
SYNCRONOUS_CLIENT = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

OPENAI_API_MODELS = [
    "gpt-4o-mini",
    "gpt-4o", 
    "gpt-4-turbo",
    "gpt-4",
    "gpt-4o",
    # "gpt-3.5-turbo",
    # "gpt-3.5",
]

async def sendMessageToLlm(messages, model_name, asyncronous=False):
    client = ASYNCRONOUS_CLIENT if asyncronous else SYNCRONOUS_CLIENT
    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
    )
    return response.choices[0].message.content

def sendCompletionToLlm(prompt, model_name, asyncronous=False):
    client = ASYNCRONOUS_CLIENT if asyncronous else SYNCRONOUS_CLIENT
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}],
    )
    return response.choices[0].message.content

def generateReport(prompt, model_name):
    reportContainer = st.container(border=True).empty()
    client = SYNCRONOUS_CLIENT
    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}],
        stream=True
    )
    streamed_text = ""
    for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text += chunk_content
            reportContainer.markdown(streamed_text)

    with st.popover("Copy"):
        st.code(streamed_text, language="markdown")

def generateRerankedConversations(df):
    df = df[["categorie", "theme", "sujet"]]
    llm_response = sendCompletionToLlm(getRerankedConversationPrompt(df.to_json()), "gpt-4-turbo", asyncronous=False)
    return extractJsonObjectFromText(llm_response)

def messagesToString(messages):
    formatted_output = []
    for message in messages:
        if message['role'] == 'user':
            formatted_output.append(f"User:\n{message['content']}\n\n")
        elif message['role'] == 'assistant':
            formatted_output.append(f"Assistant:\n{message['content']}\n\n")
    return ''.join(formatted_output)


def get_embedding(text: str, model="text-embedding-3-small", **kwargs) -> List[float]:
    text = text.replace("\n", " ")
    response = SYNCRONOUS_CLIENT.embeddings.create(input=[text], model=model, **kwargs)
    return response.data[0].embedding
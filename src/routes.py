import requests
import urllib.parse
import streamlit as st
import os
from src.prompts import reportPrompt
import asyncio
from openai import AsyncOpenAI

base_url = "https://genii-api.tolk.ai/v1/"

def getAllUsers():
    url = f"{base_url}users/{st.secrets['ADMIN_USER_ID']}/user-infos"
    response = requests.get(url)
    return response.json()

def getConversationsByProjectId(projectId, params):
    url = f"{base_url}projects/{projectId}/conversations"
    encodedParams = urllib.parse.urlencode(params)
    response = requests.get(f"{url}?{encodedParams}")
    return response.json()

def getConversationById(projectId, conversationId):
    url = f"{base_url}projects/{projectId}/conversations/{conversationId}/messages"
    response = requests.get(url)
    return response.json()

def sendMessageToLlm(messages, model_name, client):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
    )
    return response.choices[0].message.content

def sendCompletionToLlm(prompt, model_name, client):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}],
    )
    return response.choices[0].message.content

# sendCompletionToLlmWithStream
# def sendCompletionToLlmWithStream(prompt, model_name, client):
#     response = client.chat.completions.create(
#         model=model_name,
#         messages=[{"role": "system", "content": prompt}],
#         stream=True
#     )

#     for chunk in response:
#         print(chunk)
#         print(chunk.choices[0].delta.content)
#         print("****************")


async def generateReport(prompt, model_name, client, placeholder):
    stream = await client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}],
        stream=True
    )
    streamed_text = ""
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text += chunk_content
            placeholder.markdown(streamed_text)

    with st.popover("Copy"):
        st.code(streamed_text, language="markdown")
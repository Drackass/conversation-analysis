import requests
import urllib.parse
import streamlit as st
import os
from src.prompts import reportPrompt
import asyncio
from openai import AsyncOpenAI
import aiohttp

base_url = "https://genii-api.tolk.ai/v1/"
# # cette route et protégé par un barear token qui dans etre transmis au call en tant que auth

def getAllUsers():
    url = f"{base_url}users/{st.secrets['ADMIN_USER_ID']}/user-infos"
    headers = {
        "Authorization": f"Bearer {st.secrets['AUTH_TOKEN']}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# def getAllUsers():
#     url = f"{base_url}users/{st.secrets['ADMIN_USER_ID']}/user-infos"
#     response = requests.get(url)
#     return response.json()

def getConversationsByProjectId(projectId, params):
    url = f"{base_url}projects/{projectId}/conversations"
    encodedParams = urllib.parse.urlencode(params)
    response = requests.get(f"{url}?{encodedParams}")
    return response.json()

# async def getConversationById(projectId, conversationId):
#     url = f"{base_url}projects/{projectId}/conversations/{conversationId}/messages"
#     response = await requests.get(url)
#     return response.json()

async def getConversationById(projectId, conversationId):
    url = f"{base_url}projects/{projectId}/conversations/{conversationId}/messages"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
        
async def sendMessageToLlm(messages, model_name, client):
    response = await client.chat.completions.create(
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

def generateReport(prompt, model_name, client, placeholder):
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
            placeholder.markdown(streamed_text)

    with st.popover("Copy"):
        st.code(streamed_text, language="markdown")

    return streamed_text

import requests
import urllib.parse

base_url = "https://genii-api.tolk.ai/v1/"

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
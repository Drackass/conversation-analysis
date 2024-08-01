import aiohttp
import requests
import urllib.parse
import streamlit as st
import streamlit as st
import requests
import jwt
import time

AUTH_MANAGEMENT_BASE_URL = 'https://dev-auth-api.genii.dev/v1'
GENII_API_BASE_URL = 'https://genii-api.tolk.ai/v1'

def set_tokens(access_token, refresh_token):
    st.session_state['access_token'] = access_token
    st.session_state['refresh_token'] = refresh_token

def authenticate():
    if 'access_token' not in st.session_state:
        st.session_state['access_token'] = None
    if 'refresh_token' not in st.session_state:
        st.session_state['refresh_token'] = None

    response = requests.post(f"https://genii-auth-api.tolk.ai/v1/token", json={
        "grant_type": "client_credentials",
        'app_id': st.secrets['APP_ID'],
        'app_secret': st.secrets['APP_SECRET'],
        'scope': 'openid profile email'
    })

    if response.status_code == 200:
        data = response.json()
        set_tokens(data['access_token'], data['refresh_token'])

    else:
        st.error("Authentication failed")
        st.stop()

def get_access_token():
    return st.session_state['access_token']

def get_refresh_token():
    return st.session_state['refresh_token']

def remove_tokens():
    st.session_state['access_token'] = None
    st.session_state['refresh_token'] = None

def is_token_expired(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        exp = decoded_token.get('exp', 0)
        return exp <= time.time()
    except jwt.ExpiredSignatureError:
        return True
    except jwt.DecodeError:
        return True

def refresh_access_token():
    refresh_token = get_refresh_token()
    if not refresh_token:
        raise Exception("No refresh token available")
    
    response = requests.post(f"{AUTH_MANAGEMENT_BASE_URL}/token", json={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })

    if response.status_code == 200:
        data = response.json()
        set_tokens(data['access_token'], data.get('refresh_token', refresh_token))
    else:
        raise Exception("Failed to refresh access token")

def authenticated_request(method, url, **kwargs):
    if is_token_expired(get_access_token()):
        refresh_access_token()
    
    access_token = get_access_token()
    headers = kwargs.get('headers', {})
    headers['Authorization'] = f'Bearer {access_token}'
    kwargs['headers'] = headers

    response = requests.request(method, url, **kwargs)
    
    if response.status_code == 401:
        refresh_access_token()
        access_token = get_access_token()
        headers['Authorization'] = f'Bearer {access_token}'
        kwargs['headers'] = headers
        response = requests.request(method, url, **kwargs)
    
    response.raise_for_status()
    return response.json()

def getAllUsers():
    try:
        url = f'{GENII_API_BASE_URL}/users/{st.secrets["ADMIN_USER_ID"]}/user-infos'
        response = authenticated_request('GET', f"{url}")
        allUsers = [{"name": user["name"], "id": user["id"]} for user in response["projects"]] 
        return allUsers
    except Exception as e:
        st.error(f"Error: {e}", icon='❌')
        remove_tokens()

def getConversationsByProjectId(projectId, params):
    try:
        encodedParams = urllib.parse.urlencode(params)
        url = f"{GENII_API_BASE_URL}/projects/{projectId}/conversations"
        response = authenticated_request('GET', f"{url}?{encodedParams}")
        st.success(f"Fetched {len(response["data"])} conversations", icon='✅')
        return response
    except Exception as e:
        st.error(f"Error: {e}", icon='❌')

def getConversationById(projectId, conversationId):
    try:
        url = f"{GENII_API_BASE_URL}/projects/{projectId}/conversations/{conversationId}/messages"
        response = authenticated_request('GET', f"{url}")
        return response
        
    except Exception as e:
        st.error(f"Error: {e}", icon='❌')





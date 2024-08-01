```py
def getAllUsers():
    url = f"{base_url}users/{st.secrets['ADMIN_USER_ID']}/user-infos"
    headers = {
        "Authorization": f"Bearer {st.secrets['AUTH_TOKEN']}"
    }
    response = requests.get(url, headers=headers)
    return response.json()
```


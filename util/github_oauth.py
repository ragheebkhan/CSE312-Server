import requests
import util.request
import util.response
import util.database
import util.userdata
from dotenv import load_dotenv
import os
import re
import json
import uuid

load_dotenv()

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

def authgithub(request : util.request.Request, handler):
    params = {"client_id" : GITHUB_CLIENT_ID,
              "redirect_uri" : "http://localhost:8080/authcallback",
              "scope": "user:email read:user"}
    redirect_request_url = requests.Request(url="https://github.com/login/oauth/authorize",params=params).prepare().url

    res = util.response.Response()
    res.set_status(302, "Found")
    res.headers({"Location":redirect_request_url})
    handler.request.sendall(res.to_data())

def extract_code(request : util.request.Request):
    path = request.path
    try:
        code = re.search(r'(?<=[&?])code=([^&]+)', path).group(1)
        return code
    except:
        return None

def authcallback(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)
    code = extract_code(request)

    params = {"client_id" : GITHUB_CLIENT_ID,
              "client_secret" : GITHUB_CLIENT_SECRET,
              "code" : code}
    
    response = requests.post("https://github.com/login/oauth/access_token",headers={"Accept" : "application/json"}, params = params)

    token = json.loads(response.content)["access_token"]

    api_response = requests.get("https://api.github.com/user", headers={"Authorization" : f"Bearer {token}"})

    github_user_data = json.loads(api_response.content)

    username = github_user_data["login"]
    email = github_user_data["email"]

    db_username = email if email else username

    auth_token = str(uuid.uuid4())
    auth_hash = hash(auth_token)

    user_data = user_data_interface.search_by_username(db_username)

    if not user_data:
        new_user = util.userdata.UserData(str(uuid.uuid4()),db_username,auth_hash = auth_hash, auth_valid=True)
        user_data_interface.create(new_user)
    else:
        user_data_interface.update_auth_hash(user_data.user_id, auth_hash)
        user_data_interface.update_auth_validity(user_data.user_id, True)

    res = util.response.Response()
    res.set_status(302,"Found")
    res.headers({"Location":"/"})
    res.cookies({"auth_token" : f"{auth_token}; HttpOnly; Max-Age=3600;"})
    handler.request.sendall(res.to_data())

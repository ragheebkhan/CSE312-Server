import re
import util.response
import util.request
import util.database
import bcrypt
import uuid
import util.userdata

def percent_decode(encoded_string : str):
    encoding_map = {"%21" : "!",
                    "%23" : "#",
                    "%24" : "$",
                    "%25" : "%",
                    "%26" : "&",
                    "%27" : "'",
                    "%28" : "(",
                    "%29" : ")",
                    "%2A" : "*",
                    "%2B" : "+",
                    "%2C" : ",",
                    "%2F" : "/",
                    "%3A" : ":",
                    "%3B" : ";",
                    "%3D" : "=",
                    "%3F" : "?",
                    "%40" : "@",
                    "%5B" : "[",
                    "%5D" : "]"}
    
    encoded_pattern = re.compile(r"%21|%23|%24|%25|%26|%27|%28|%29|%2A|%2B|%2C|%2F|%3A|%3B|%3D|%3F|%40|%5B|%5D")
    return encoded_pattern.sub(lambda match: encoding_map[match.group(0)], encoded_string)

def extract_credentials(request : util.request.Request):
    body = request.body.decode()

    try:
        username=re.search(r'(?:(?<=^)|(?<=&))username=([a-zA-Z0-9]+)', body).group(1)
        password=re.search(r'(?:(?<=^)|(?<=&))password=([^&]+)',body).group(1)
        password = percent_decode(password)
        return [username,password]
    except:
        return []

    
def validate_password(password : str):
    if len(password) < 8:
        return False
    
    if not re.search(r'[a-z]',password):
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[0-9]', password):
        return False
    
    if not re.search(r'[!@#$%^&()\-_=]', password):
        return False
    
    if re.search(r'[^a-zA-Z0-9!@#$%^&()\-_=]', password):
        return False
    
    return True

def register(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)

    username = ""
    password = ""

    try:
        username, password = extract_credentials(request)
        if not validate_password(password):
            raise Exception()
    except:
        util.response.send400(handler, "Invalid password")
        return
    
    if user_data_interface.search_by_username(username):
        util.response.send400(handler, "Username already taken")
        return
    
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt)

    userdata = util.userdata.UserData()
    userdata.user_id = str(uuid.uuid4())
    userdata.username = username
    userdata.password_hash = password_hash

    user_data_interface.create(userdata)
    
    util.response.send200(handler, "Registration Successful")

def login(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)

    username = ""
    password = ""

    try:
        username, password = extract_credentials(request)
        if not validate_password(password):
            raise Exception()
    except:
        util.response.send400(handler, "Invalid username or password")
        return
    
    userdata = user_data_interface.search_by_username(username)

    if not userdata:
        util.response.send400(handler, "Username does not exist")
        return
    
    if not bcrypt.checkpw(password.encode(), userdata.password_hash):
        util.response.send400(handler, "Incorrect Password")
        return
    
    auth_token = str(uuid.uuid4())
    auth_hash = hash(auth_token)

    user_data_interface.update_auth_hash(userdata.user_id, auth_hash)
    user_data_interface.update_auth_validity(userdata.user_id,True)

    res = util.response.Response()
    res.cookies({"auth_token":f"{auth_token}; HttpOnly; Max-Age=3600;"})
    handler.request.sendall(res.to_data())

def logout(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)

    if "auth_token" not in request.cookies:
        util.response.send400(handler, "No auth token")
        return
    
    auth_token = request.cookies["auth_token"]

    auth_hash = hash(auth_token)

    userdata = user_data_interface.search_by_auth_hash(auth_hash)

    if not userdata:
        util.response.send400(handler, "No user found")
        return
    
    user_data_interface.update_auth_validity(userdata.user_id, False)

    res = util.response.Response()
    res.set_status(302, "Found")
    res.headers({"Location":"/"})
    res.cookies({"auth_token":f"{auth_token}; HttpOnly; Max-Age=0;"})

    handler.request.sendall(res.to_data())

def get_user(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)

    if "auth_token" not in request.cookies:
        res = util.response.Response()
        res.set_status(401, "Unauthorized")
        res.json({})
        handler.request.sendall(res.to_data())
        return
    
    auth_hash = hash(request.cookies["auth_token"])

    userdata = user_data_interface.search_by_auth_hash(auth_hash)

    if not userdata:
        res = util.response.Response()
        res.set_status(401, "Unauthorized")
        res.json({})
        handler.request.sendall(res.to_data())
        return
    
    if not userdata.auth_valid:
        res = util.response.Response()
        res.set_status(401, "Unauthorized")
        res.json({})
        handler.request.sendall(res.to_data())
        return
    
    res = util.response.Response()

    res.json({"username":userdata.username, "id":userdata.user_id})

    handler.request.sendall(res.to_data())

def update_profile(request : util.request.Request, handler):
    pass
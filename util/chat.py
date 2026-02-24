import util.database
import util.request
import util.response
import uuid
import json
import util.userdata
import random

def gen_guest_name():
    digit1 = str(random.randint(0,9))
    digit2 = str(random.randint(0,9))
    digit3 = str(random.randint(0,9))
    digit4 = str(random.randint(0,9))
    digit5 = str(random.randint(0,9))
    digit6 = str(random.randint(0,9))
    name = "Guest-"+digit1+digit2+digit3+digit4+digit5+digit6
    return name

def escape_html(text : str):
    newstr = text.replace("&", "&amp;")
    newstr = newstr.replace("<", "&lt;")
    newstr = newstr.replace(">", "&gt;")
    return newstr

def create_guest_message(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)
    chats = util.database.chat_collection

    author = ""
    session = ""
    nickname = None
    message_id = str(uuid.uuid4())
    content = escape_html(json.loads(request.body)["content"])

    try:
        session = request.cookies["session"]
        userdata = user_data_interface.search_by_session(session)
        author = userdata.username
        if userdata.nickname != "":
            nickname = userdata.nickname
    except:
        while author == "":
            generated_name = gen_guest_name()
            userdata = user_data_interface.search_by_username(generated_name)
            if userdata:
                continue
            else:
                author = generated_name
        session = str(uuid.uuid4())

        userdata = util.userdata.UserData(str(uuid.uuid4()),author,session=session)
        user_data_interface.create(userdata)

    if nickname:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}, "nickname":nickname})
    else:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}})

    res = util.response.Response()
    res.text("Message Sent")
    res.cookies({"session":session})
    handler.request.sendall(res.to_data())

def create_user_message(request : util.request.Request, user_data : util.userdata.UserData, handler):
    chats = util.database.chat_collection

    author = user_data.username
    nickname = None if user_data.nickname == "" else user_data.nickname
    message_id = str(uuid.uuid4())
    content = escape_html(json.loads(request.body)["content"])

    if nickname:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}, "nickname":nickname})
    else:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}})

    res = util.response.Response()
    res.text("Message Sent")
    handler.request.sendall(res.to_data())
    
def create_message(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)

    if "auth_token" in request.cookies:
        auth_token = request.cookies["auth_token"]
        auth_hash = hash(auth_token)
        user_data = user_data_interface.search_by_auth_hash(auth_hash)
        if not user_data:
            create_guest_message(request, handler)
            return
        if not user_data.auth_valid:
            create_guest_message(request, handler)
            return
        create_user_message(request, user_data, handler)
    else:
        create_guest_message(request, handler)

def get_messages(request : util.request.Request, handler):
    chats = util.database.chat_collection

    messages = []

    entries = chats.find({})

    for entry in entries:
        if "nickname" in entry:
            messages.append({"author":entry["author"], "id":entry["id"], "content":entry["content"], "updated":entry["updated"], "reactions":entry["reactions"],"nickname":entry["nickname"]})
        else:
            messages.append({"author":entry["author"], "id":entry["id"], "content":entry["content"], "updated":entry["updated"], "reactions":entry["reactions"]})

    body = {"messages": messages}

    res = util.response.Response()
    res.json(body)

    handler.request.sendall(res.to_data())

def find_user_data(request : util.request.Request):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)
    user_data = None

    if "auth_token" in request.cookies:
        auth_token = request.cookies["auth_token"]
        auth_hash = hash(auth_token)
        user_data = user_data_interface.search_by_auth_hash(auth_hash)
        if not user_data:
            user_data = None
        if user_data and not user_data.auth_valid:
            user_data = None

    if user_data:
        return user_data
    
    if "session" in request.cookies:
        session = request.cookies["session"]
        user_data = user_data_interface.search_by_session(session)
        if not user_data:
            return None
    else:
        return None
    
    return user_data

def update_message(request : util.request.Request, handler):
    chats = util.database.chat_collection

    user_data = find_user_data(request)

    if not user_data:
        util.response.send403(handler, "user not found")
        return

    msgid = request.path.lstrip("/api/chats/")
    content = json.loads(request.body)["content"]
    content = escape_html(content)
    
    msg = chats.find_one({"id":msgid})

    if not msg:
        util.response.send404(handler)
        return
    
    if msg["author"] != user_data.username:
        util.response.send403(handler)
        return
    
    chats.update_one({"id":msgid},{"$set":{"content":content,"updated":True}})

    res = util.response.Response()
    res.text("Message Updated Successfully")
    handler.request.sendall(res.to_data())

def delete_message(request : util.request.Request, handler):
    chats = util.database.chat_collection

    user_data = find_user_data(request)

    if not user_data:
        util.response.send403(handler)
        return

    msgid = request.path.lstrip("/api/chats/")
    
    msg = chats.find_one({"id":msgid})

    if not msg:
        util.response.send404(handler)
        return
    
    if msg["author"] != user_data.username:
        util.response.send403(handler)
        return
    
    chats.delete_one({"id":msgid})

    res = util.response.Response()
    res.text("Message deleted Successfully")
    handler.request.sendall(res.to_data())

def add_reaction(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)
    chats = util.database.chat_collection

    user_data = find_user_data(request)

    if not user_data:
        user_data = util.userdata.UserData(str(uuid.uuid4()), gen_guest_name(), session=str(uuid.uuid4()))
        user_data_interface.create(user_data)
    
    msgid = request.path.lstrip("/api/reaction/")
    emoji = json.loads(request.body)["emoji"]

    message = chats.find_one({"id":msgid})

    if message == None:
        util.response.send404(handler, "Message Not Found")
        return
    
    reactions = message["reactions"]

    if emoji not in reactions:
        reactions[emoji] = []

    if user_data.username in reactions[emoji]:
        util.response.send403(handler)
        return
    
    reactions[emoji].append(user_data.username)

    chats.update_one({"id":msgid},{"$set":{"reactions":reactions}})

    res = util.response.Response()
    res.text("Reaction Added Successfully")
    res.cookies({"session" : user_data.session})
    handler.request.sendall(res.to_data())

def remove_reaction(request : util.request.Request, handler):
    user_data = find_user_data(request)
    chats = util.database.chat_collection

    if not user_data:
        util.response.send403(handler)
        return
    
    msgid = request.path.lstrip("/api/reaction/")
    emoji = json.loads(request.body)["emoji"]

    message = chats.find_one({"id":msgid})

    if message == None:
        util.response.send404(handler, "Message Not Found")
        return
    
    reactions = message["reactions"]

    if emoji not in reactions:
        util.response.send403(handler)
        return

    if user_data.username not in reactions[emoji]:
        util.response.send403(handler)
        return
    
    reactions[emoji].remove(user_data.username)

    if reactions[emoji] == []:
        del reactions[emoji]
    
    chats.update_one({"id":msgid}, {"$set":{"reactions":reactions}})

    res = util.response.Response()
    res.text("Reaction Deleted Successfully")
    handler.request.sendall(res.to_data())

def edit_nickname(request : util.request.Request, handler):
    user_data_interface = util.userdata.UserDataInterface(util.database.user_collection)
    user_data = find_user_data(request)

    res = util.response.Response()
    res.text("Nickname Updated Successfully")

    if not user_data:
        print("CREATING USER")
        user_data = util.userdata.UserData(str(uuid.uuid4()), gen_guest_name(), session=str(uuid.uuid4()))
        user_data_interface.create(user_data)
        res.cookies({"session":user_data.session})
    
    chats = util.database.chat_collection

    nickname = json.loads(request.body)["nickname"]
    nickname = escape_html(nickname)

    user_data_interface.update_nickname(user_data.user_id, nickname)

    chats.update_many({"author":user_data.username}, {"$set" : {"nickname":nickname}})
    handler.request.sendall(res.to_data())
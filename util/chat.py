import util.database
import util.request
import util.response
import uuid
import json

def escape_html(text : str):
    newstr = text.replace("&", "&amp;")
    newstr = newstr.replace("<", "&lt;")
    newstr = newstr.replace(">", "&gt;")
    return newstr

def create_message(request : util.request.Request, handler):
    chats = util.database.chat_collection
    users = util.database.user_collection

    content = json.loads(request.body)["content"]
    content = escape_html(content)

    message_id = str(uuid.uuid4())
    author = ""
    session = ""

    if "session" not in request.cookies:
        session = str(uuid.uuid4())
        author = str(uuid.uuid4())
        users.insert_one({"session" : session, "author" : author})
    else:
        session = request.cookies["session"]
        author = users.find_one({"session" : session})["author"]

    user = users.find_one({"session":session})

    if "nickname" in user:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}, "nickname":user["nickname"]})
    else:
        chats.insert_one({"author" : author, "id":message_id, "content":content, "updated":False, "reactions":{}})

    res = util.response.Response()
    res.cookies({"session" : session})
    res.text("Message Sent")

    handler.request.sendall(res.to_data())

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

def update_message(request : util.request.Request, handler):
    if "session" not in request.cookies:
        util.response.send403(handler)
        return

    session = request.cookies["session"]

    msgid = request.path.lstrip("/api/chats/")
    content = json.loads(request.body)["content"]
    content = escape_html(content)

    chats = util.database.chat_collection
    users = util.database.user_collection

    msg = chats.find_one({"id":msgid})
    if msg == None:
        util.response.send404(handler)
        return
    
    original_author = msg["author"]

    orig_session = users.find_one({"author":original_author})

    if orig_session == None:
        util.response.send404(handler)
        return
    orig_session = orig_session["session"]

    if session != orig_session:
        util.response.send403(handler)
        return
    
    chats.update_one({"id":msgid},{"$set":{"content":content,"updated":True}})

    res = util.response.Response()
    res.text("Message Updated Successfully")
    handler.request.sendall(res.to_data())

def delete_message(request : util.request.Request, handler):
    if "session" not in request.cookies:
        util.response.send403(handler)
        return

    session = request.cookies["session"]

    msgid = request.path.lstrip("/api/chats/")

    chats = util.database.chat_collection
    users = util.database.user_collection

    msg = chats.find_one({"id":msgid})
    if msg == None:
        util.response.send404(handler)
        return
    
    original_author = msg["author"]

    orig_session = users.find_one({"author":original_author})

    if orig_session == None:
        util.response.send404(handler)
        return
    orig_session = orig_session["session"]

    if session != orig_session:
        util.response.send403(handler)
        return
    
    chats.delete_one({"id":msgid})

    res = util.response.Response()
    res.text("Message Deleted Successfully")
    handler.request.sendall(res.to_data())

def add_reaction(request : util.request.Request, handler):
    chats = util.database.chat_collection
    users = util.database.user_collection
    session = ""
    if "session" not in request.cookies:
        session = str(uuid.uuid4())
        author = str(uuid.uuid4())
        users.insert_one({"session":session, "author":author})
    else:
        session = request.cookies["session"]
    
    msgid = request.path.lstrip("/api/reaction/")
    emoji = json.loads(request.body)["emoji"]

    message = chats.find_one({"id":msgid})

    if message == None:
        util.response.send404(handler, "Message Not Found")
        return
    
    reactions = message["reactions"]

    if emoji not in reactions:
        reactions[emoji] = []

    if session in reactions[emoji]:
        util.response.send403(handler)
        return
    
    reactions[emoji].append(session)

    chats.update_one({"id":msgid},{"$set":{"reactions":reactions}})

    res = util.response.Response()
    res.text("Reaction Added Successfully")
    res.cookies({"session":session})
    handler.request.sendall(res.to_data())

def remove_reaction(request : util.request.Request, handler):
    if "session" not in request.cookies:
        util.response.send403(handler)
        return
    
    chats = util.database.chat_collection
    session = request.cookies["session"]
    msgid = request.path.lstrip("/api/reaction/")
    emoji = json.loads(request.body)["emoji"]

    message = chats.find_one({"id":msgid})

    if message == None:
        util.response.send404(handler, "Message Not Found")
    
    reactions = message["reactions"]

    if emoji not in reactions:
        util.response.send403(handler)
    if session not in reactions[emoji]:
        util.response.send403(handler)
    
    reactions[emoji].remove(session)
    if reactions[emoji] == []:
        del reactions[emoji]
    
    chats.update_one({"id":msgid}, {"$set":{"reactions":reactions}})

    res = util.response.Response()
    res.text("Reaction Deleted Successfully")
    handler.request.sendall(res.to_data())

def edit_nickname(request : util.request.Request, handler):
    chats = util.database.chat_collection
    users = util.database.user_collection
    session = ""
    author = ""
    if "session" not in request.cookies:
        session = str(uuid.uuid4())
        author = str(uuid.uuid4())
        users.insert_one({"session":session, "author":author})
    else:
        session = request.cookies["session"]
        author = users.find_one({"session":session})["author"]

    nickname = json.loads(request.body)["nickname"]
    nickname = escape_html(nickname)

    users.update_one({"session":session},{"$set":{"nickname":nickname}})

    chats.update_many({"author":author}, {"$set" : {"nickname":nickname}})

    res = util.response.Response()
    res.text("Nickname Updated Successfully")
    res.cookies({"session":session})
    handler.request.sendall(res.to_data())
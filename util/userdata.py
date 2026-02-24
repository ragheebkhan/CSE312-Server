from pymongo.collection import Collection
from dataclasses import dataclass

@dataclass
class UserData:
    user_id : str = ""
    username : str = ""
    nickname : str = ""
    password_hash : bytes = b""
    auth_hash : int = 0
    auth_valid : bool = False
    session : str = ""

class UserDataInterface:
    def __init__(self, user_collection : Collection):
        self.__user_collection = user_collection

    def __from_record(self, record):
        userdata = UserData()
        userdata.user_id = record["user_id"]
        userdata.username = record["username"]
        userdata.nickname = record["nickname"]
        userdata.password_hash = record["password_hash"]
        userdata.auth_hash = record["auth_hash"]
        userdata.auth_valid = record["auth_valid"]
        userdata.session = record["session"]
        return userdata
    
    def search_by_username_prefix(self, prefix):
        results = []
        all_users = self.__user_collection.find({})

        for user in all_users:
            if user["username"].startswith(prefix):
                results.append(self.__from_record(user))
        return results
    
    def search_by_user_id(self, user_id : str):
        record = self.__user_collection.find_one({"user_id":user_id})

        if not record:
            return None
        
        return self.__from_record(record)
    
    def search_by_username(self, username):
        record = self.__user_collection.find_one({"username":username})

        if not record:
            return None
        
        return self.__from_record(record)
    
    def search_by_session(self, session):
        record = self.__user_collection.find_one({"session":session})

        if not record:
            return None
        
        return self.__from_record(record)
    
    def search_by_auth_hash(self, auth_hash):
        record = self.__user_collection.find_one({"auth_hash":auth_hash})

        if not record:
            return None
        
        return self.__from_record(record)
    
    def create(self, userdata : UserData):
        if userdata.user_id == "":
            raise Exception("userdata must have user_id")
        
        if self.__user_collection.find_one({"user_id" : userdata.user_id}):
            raise Exception(f"User with id {userdata.user_id} already exists")
        
        if self.__user_collection.find_one({"username" : userdata.username}):
            raise Exception(f"User with username {userdata.username} already exists")
        
        self.__user_collection.insert_one({"user_id":userdata.user_id,
                                           "username" : userdata.username,
                                           "nickname" :userdata.nickname,
                                           "password_hash":userdata.password_hash,
                                           "auth_hash":userdata.auth_hash,
                                           "auth_valid":userdata.auth_valid,
                                           "session":userdata.session})
        
    def delete_by_id(self, user_id):
        return self.__user_collection.delete_one({"user_id":user_id})

    def delete_by_username(self, username):
        return self.__user_collection.delete_one({"username":username})

    def update_username(self, user_id, new_username):
        other = self.__user_collection.find_one({"username":new_username})
        if other and other["user_id"] != user_id:
            raise Exception(f"Username {new_username} already exists")
        
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"username":new_username}})
    
    def update_nickname(self, user_id, new_nickname):
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"nickname":new_nickname}})
    
    def update_password_hash(self, user_id, new_password_hash : bytes):
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"password_hash":new_password_hash}})
    
    def update_auth_hash(self, user_id, new_auth_hash : int):
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"auth_hash":new_auth_hash}})
    
    def update_auth_validity(self, user_id, new_validity : bool):
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"auth_valid":new_validity}})
    
    def update_session(self, user_id, new_session):
        return self.__user_collection.update_one({"user_id":user_id}, {"$set":{"session":new_session}})


        
    
    


        
        


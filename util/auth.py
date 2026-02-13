import util.request
import re

def extract_credentials(request : util.request.Request):
    body = request.body.decode()

    match = re.search(r'username=([a-zA-Z0-9]+)&password=(.+)',body,re.DOTALL)

    if match:
        return [match.group(1), match.group(2)]
    else:
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
    
    if re.search(r'[^a-zA-Z0-9!@#$%^&()\-_=]'):
        return False
    
    return True

    
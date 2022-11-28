import hashlib
import datetime
import jwt
import os
from fastapi import FastAPI, Header, Response, status, HTTPException, Request

SECRET = "TSTGemink"

# for hashing password
def get_hash(string):
    if (type(string) is str):
        message = string.encode()
        return hashlib.sha256(message).hexdigest()
    else:
        return None
    
# Make jwt token from credentials
def encode_token(username):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days = 3),
            'iat': datetime.datetime.utcnow(),
            'username': username
        }
        return jwt.encode(
            payload,
            SECRET
        )
    except Exception as e:
        return e
    
def authorize(request: Request):
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload.get('username')
    except:
        raise HTTPException(status_code = 401, detail = "Token invalid, coba login lagi ya!")
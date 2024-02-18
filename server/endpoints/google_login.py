
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
import requests
import os
from flask_jwt_extended import create_access_token
import redis


load_dotenv(find_dotenv())


r = redis.Redis(
host=os.environ["REDIS_HOST"],
port=11866,
password=os.environ["REDIS_PASSWORD"])

def login():
    auth_code = request.get_json()['code']
    data = {
        'code': auth_code,
        'client_id': os.environ["GOOGLE_CLIENT_ID"],  # client ID from the credential at google developer console
        'client_secret': os.environ["GOOGLE_SECRET_KEY"],  # client secret from the credential at google developer console
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data).json()
    
    headers = {
        'Authorization': f'Bearer {response["access_token"]}'
    }
    user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers=headers).json()

    # USE REDIS TO CREATE A KEY VALUE MAPPING FROM THE REFRESH TOKEN TO THE SESSION TOKEN
    # print("STARTING REDIS")
    # print(r.ping())
    # # r.set(response["refresh_token"],response["access_token"])
    # print("DONE WITH REDIS")

    # response.pop('access_token', None)
    response['user_info'] = user_info
    

    return response, 200


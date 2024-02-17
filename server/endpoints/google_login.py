
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
import requests
import os
from flask_jwt_extended import create_access_token

load_dotenv(find_dotenv())


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

    jwt_token = create_access_token(identity=user_info['email'])  
    print(jwt_token)
    response.set_cookie('access_token_cookie', value=jwt_token, httponly=True, secure=False, samesite='Lax')
    response.headers['Authorization'] = jwt_token

    return response, 200


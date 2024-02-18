from flask import Flask,jsonify,request
from flask_cors import CORS
from endpoints.test import handle_test
from endpoints.google_login import login
from endpoints.process_audio import handle_audio,handle_execute
from dotenv import load_dotenv, find_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import os
load_dotenv(find_dotenv())


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET"]
app.config['JWT_TOKEN_LOCATION'] = ['cookies']


CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.add_url_rule('/test', 'handle_test', handle_test, methods=['POST'])
app.add_url_rule('/google_login', 'login', login, methods=['POST'])


@app.route("/protected", methods=["POST"])
def protected():
    response={"data":"You are a dumb stupid fucker and I will not help you."}
    # request_data = request.get_json()  
    # profile = request_data.get('profile')
    # print(profile)
    # credentials = Credentials(token=profile["access_token"])

    # print(credentials)
    
    # # Build the Google Calendar API service
    # service = build('calendar', 'v3', credentials=credentials)
    
    # # Call the Calendar API to list the user's calendars
    # calendar_list = service.calendarList().list().execute()
    
    # # Print the calendars or return them
    # for calendar in calendar_list['items']:
    #     print(calendar['summary'])
    return response, 200

app.add_url_rule('/process-audio', 'handle_execute', handle_execute, methods=['POST'])

if __name__ == '__main__':
    app.run(port=5000)
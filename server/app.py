from flask import Flask,jsonify,request
from flask_cors import CORS
from endpoints.test import handle_test
from endpoints.google_login import login
from endpoints.process_audio import handle_audio
from dotenv import load_dotenv, find_dotenv
from flask_jwt_extended import  JWTManager, jwt_required, get_jwt_identity


import os
load_dotenv(find_dotenv())


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.environ["JWT_SECRET"]
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
jwt = JWTManager(app)

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.add_url_rule('/test', 'handle_test', handle_test, methods=['POST'])
app.add_url_rule('/google_login', 'login', login, methods=['POST'])


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    jwt_token = request.cookies.get('access_token_cookie') # Demonstration how to get the cookie
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

app.add_url_rule('/process-audio', 'handle_audio', handle_audio, methods=['POST'])

if __name__ == '__main__':
    app.run(port=5000)
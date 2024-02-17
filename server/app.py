from flask import Flask
from flask_cors import CORS
from server.endpoints.test import handle_test
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.add_url_rule('/test', 'handle_test', handle_test, methods=['POST'])


if __name__ == '__main__':
    app.run(port=3001)
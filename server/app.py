from flask import Flask
from flask_cors import CORS
from endpoints.test import handle_test
from endpoints.process_audio import handle_audio
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.add_url_rule('/test', 'handle_test', handle_test, methods=['POST'])
app.add_url_rule('/process-audio', 'handle_audio', handle_audio, methods=['POST'])

if __name__ == '__main__':
    app.run(port=5000)
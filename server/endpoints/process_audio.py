
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

API_URL = os.environ["API_URL"]
HF_API_TOKEN = os.environ["HF_API_TOKEN"]

# Define headers using the environment variables
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {HF_API_TOKEN}",  # Use the loaded API token
    "Content-Type": "audio/flac"  # Ensure this matches the content type of the audio you're sending
}



def handle_audio():
    audio_data = request.data  # Directly use the binary data from the request
    print("data",request.data)
    if not audio_data:
        return jsonify({'error': 'No audio data received'}), 400

    # Forward the audio data to the Hugging Face API
    response = requests.post(API_URL, headers=headers, data=audio_data)
    
    if response.status_code == 200:
        print(response.json())
        return response.json()  # Return the Hugging Face API response
    else:
        return jsonify({'error': 'Failed to process audio'}), response.status_code


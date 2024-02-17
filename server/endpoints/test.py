
from flask import Flask, request, jsonify

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def handle_test():
    return jsonify({"test": "passed"}), 200


import os
import speech_recognition as sr
from enum import Enum
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from modules.companion import Companion

app = Flask(__name__)

class ProcessInputStatus(Enum):
    SAY = 0
    LOG = 1
    EXIT = 2

def load_keys_from_env():
    load_dotenv()
    return os.environ.get('OPENAI_API_KEY'), os.environ.get('ELEVENLABS_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.json['user_input']
    response = companion.process_input(user_input, is_voice=True)
    return jsonify({'status': response.status.name, 'response': response.response})

if __name__ == '__main__':
    openai_api_key, elevenlabs_api_key = load_keys_from_env()
    env_dict = {
        'openai_api_key': openai_api_key,
        'elevenlabs_api_key': elevenlabs_api_key
    }
    args_dict = {
        'openai_api_key': openai_api_key,
        'elevenlabs_api_key': elevenlabs_api_key,
        'debug': False
    }
    companion = Companion(args_dict)
    app.run()

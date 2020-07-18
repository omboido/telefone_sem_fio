from flask import Flask, escape, render_template, request
from flask_socketio import SocketIO
#from dictation import start_stream
from reading import start_reading
from dic import start_stream
import time
import requests
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import configparser

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('audioMessage')
def handle_message(audioMessage):
    start_stream(audioMessage)

@app.route('/')
def index():
	return render_template('ouvir.html')

if __name__ == "__main__":
    socketio.run(app)
    #app.run(host="127.0.0.1", port="5000", debug=True)
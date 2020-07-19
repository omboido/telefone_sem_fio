from flask import Flask, escape, render_template, request
from flask_socketio import SocketIO
#from dictation import start_stream
from reading import start_reading
from dic import start_stream
import time
import requests
from requests.auth import HTTPBasicAuth
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import configparser
import json

app = Flask(__name__)
socketio = SocketIO(app)
config = configparser.ConfigParser()
config.read('config.ini')

@socketio.on('audioMessage')
def handle_message(audioMessage):
    start_stream(audioMessage)

@app.route('/')
def index():
	return render_template('ouvir.html')

if __name__ == "__main__":
    socketio.run(app)
    #app.run(host="127.0.0.1", port="5000", debug=True)

# @app.route('/interpretar', methods= ['GET','POST'])
# def interpretar():

#     print('chegou em interpretar')
#     data = request.data
#     print(type(data))
    
#     """curl -X POST -u "apikey:{apikey}"
#     --header "Content-Type: audio/flac"
#     --data-binary @{path}audio-file.flac
#     "{url}/v1/recognize"
#     """

#     " WATSON_STT_APIKEY=YOUR_API_KEY"

#     #auth_var = HTTPBasicAuth('WATSON_STT_APIKEY', config['SPEECH2TEXT']['API_KEY'])
#     auth_var = HTTPBasicAuth('apikey', config['SPEECH2TEXT']['API_KEY'])

#     #?model=en-US_NarrowbandModel pt-BR_NarrowbandModel

#     x = requests.post( 
#         (config['SPEECH2TEXT']['URL'] + '/v1/recognize?model=pt-BR_NarrowbandModel'), 
#         auth=auth_var,
#         data = data, 
#         headers = {"Content-Type": "audio/ogg; codecs=opus"})

#     print('texto:')
#     json_resposta = x.text
#     print(json_resposta)
#     print('interpretacao')

#     interpretacao = json.loads(json_resposta, encoding='utf-8')['results'][0 ]['alternatives'][0]['transcript']
#     print(interpretacao)

#     '''curl -X POST -u "apikey:{apikey}" 
#     --header "Content-Type: application/json" 
#     --header "Accept: audio/wav" 
#     --data "{\"text\":\"Hello world\"}" 
#     --output hello_world.wav "{url}/v1/synthesize?voice=en-US_AllisonV3Voice"'''


#     #auth_var = HTTPBasicAuth('WATSON_STT_APIKEY', config['SPEECH2TEXT']['API_KEY'])
#     auth_var = HTTPBasicAuth('apikey', config['TEXT2SPEECH']['API_KEY'])

#     #?model=en-US_NarrowbandModel pt-BR_NarrowbandModel

#     print("como ficou:")
#     print("{\"text\":\"" + interpretacao + "\"}")

#     fala = requests.post( 
#         (config['TEXT2SPEECH']['URL'] + '/v1/synthesize?voice=pt-BR_IsabelaV3Voice'), #pt-BR_IsabelaV3Voice
#         auth=auth_var,
#         data = "{\"text\":\"" + interpretacao + "\"}",
#         #data = "\{\"text\":\"" + interpretacao + "\"}",
#         #data = interpretacao, 
#         #headers = {"Content-Type": "application/json", "Accept":"audio/wav"})
#         headers = {"Content-Type": "application/json", "Accept":"audio/ogg; codecs=opus"})
#         #headers = {"Content-Type": "text/plain", "Accept":"audio/ogg; codecs=opus"})
#         #headers = {"Content-Type": "audio/ogg; codecs=opus"})
#     print("resposta do text2speech - tipo: ")
#     print(type(fala))
#     #print(type(fala.content))
#     print(type(fala.encoding))
#     #print(fala.text)
#     print(fala.headers)
#     print(fala.status_code)

#     with open("exemplo_fala.ogg", "wb") as f:
#         f.write(fala.content)


#     return render_template("mostrar_audio.html", myBlob = fala.content)

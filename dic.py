from __future__ import print_function
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from threading import Thread
import configparser
import time
import json
import requests
from requests.auth import HTTPBasicAuth

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full

#carrega configuracoes
config = configparser.ConfigParser()
config.read('config.ini')

###############################################
#### inicia fila para gravar as gravacoes do microfone ##
###############################################
CHUNK = 1024
# Nota: gravacoes sao descartadas caso o websocket nao consuma rapido o suficiente
# Caso precise, aumente o max size conforme necessario
BUF_MAX_SIZE = CHUNK * 10
# Buffer para guardar o audio
q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))

# Cria o audio source com a fila
# audio_source = AudioSource(q, True, True)

#configura o speech2text
authenticator = IAMAuthenticator(config['SPEECH2TEXT']['API_KEY'])
speech_to_text = SpeechToTextV1(
   authenticator=authenticator)
speech_to_text.set_service_url(config['SPEECH2TEXT']['URL'])

texto = ''

# classe de callback para o servico de reconhecimento de voz
class MyRecognizeCallback(RecognizeCallback):
    
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        global texto
        print('transcript: ', transcript[0]['transcript'])
        texto = transcript[0]['transcript']
        pass

    def on_connected(self):
        print('Conexão OK')

    def on_error(self, error):
        print('Erro recebido: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Timeout de inatividade: {}'.format(error))

    def on_listening(self):
        print('Serviço está ouvindo, aperte q + Enter para finalizar')

    def on_hypothesis(self, hypothesis):
        pass

    def on_data(self, data):
        #global resultado
        print('Texto detectado: ')
        #for result in data['results']:
        #    resultado = (result['alternatives'][0]['transcript']) #Como gravar essa saída para uso na função start_reading em tsf.py?
        

    def on_close(self):
        print("Conexão fechada")


# inicia o reconhecimento usando o audio_source
def recognize_using_websocket(recorded):
    audio_source = AudioSource(recorded, False, False)
    mycallback = MyRecognizeCallback()
    speech_to_text.recognize_using_websocket(audio=audio_source,
                                             content_type='audio/webm; codecs=opus',
                                             recognize_callback=mycallback,
                                             model='pt-BR_NarrowbandModel',
                                             interim_results=False)

###############################################
#### Prepara gravacao usando pyaudio ##
###############################################

# Config do pyaudio para as gravacoes
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# define callback para gravar o audio na fila
def pyaudio_callback(in_data, frame_count, time_info, status):
    try:
        q.put(in_data)
    except Full:
        pass # discard
    return (None, pyaudio.paContinue)

def start_stream(recorded):
    print('<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>')
    print(type(recorded[0]))
    #auth_var = HTTPBasicAuth('WATSON_STT_APIKEY', config['SPEECH2TEXT']['API_KEY'])
    auth_var = HTTPBasicAuth('apikey', config['SPEECH2TEXT']['API_KEY'])

    #?model=en-US_NarrowbandModel pt-BR_NarrowbandModel

    x = requests.post( 
        (config['SPEECH2TEXT']['URL'] + '/v1/recognize?model=pt-BR_NarrowbandModel'), 
        auth=auth_var,
        data = recorded[0], 
        headers = {"Content-Type": "audio/webm; codecs=opus"})

    print('texto:')
    json_resposta = x.text
    print(json_resposta)
    print('interpretacao')

    interpretacao = json.loads(json_resposta, encoding='utf-8')['results'][0 ]['alternatives'][0]['transcript']
    print(interpretacao)

    auth_var = HTTPBasicAuth('apikey', config['TEXT2SPEECH']['API_KEY'])

    #?model=en-US_NarrowbandModel pt-BR_NarrowbandModel

    print("como ficou:")
    print("{\"text\":\"" + interpretacao + "\"}")

    fala = requests.post( 
        (config['TEXT2SPEECH']['URL'] + '/v1/synthesize?voice=pt-BR_IsabelaV3Voice'), #pt-BR_IsabelaV3Voice
        auth=auth_var,
        data = "{\"text\":\"" + interpretacao + "\"}",
        #data = "\{\"text\":\"" + interpretacao + "\"}",
        #data = interpretacao, 
        #headers = {"Content-Type": "application/json", "Accept":"audio/wav"})
        headers = {"Content-Type": "application/json", "Accept":"audio/mp3; codecs=opus"})
        #headers = {"Content-Type": "text/plain", "Accept":"audio/ogg; codecs=opus"})
        #headers = {"Content-Type": "audio/ogg; codecs=opus"})
    print("resposta do text2speech - tipo: ")
    print(type(fala))
    #print(type(fala.content))
    print(type(fala.encoding))
    #print(fala.text)
    print(fala.headers)
    print(fala.status_code)

    with open("fala.mp3", "wb") as f:
        f.write(fala.content)
    
from __future__ import print_function
import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from threading import Thread
import configparser
import time
from chardet import detect
import json
import base64

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

def guess_encoding(csv_file):
    """guess the encoding of the given file"""
    import io
    import locale
    with io.open(csv_file, "rb") as f:
        data = f.read(5)
    if data.startswith(b"\xEF\xBB\xBF"):  # UTF-8 with a "BOM"
        return "utf-8-sig"
    elif data.startswith(b"\xFF\xFE") or data.startswith(b"\xFE\xFF"):
        return "utf-16"
    else:  # in Windows, guessing utf-8 doesn't work, so we have to try
        try:
            with io.open(csv_file, encoding="utf-8") as f:
                preview = f.read(222222)
                return "utf-8"
        except:
            return locale.getdefaultlocale()[1]

def start_stream(recorded):
    print(recorded)
    with open(recorded.decode('cp437'), 'rb') as blob:
        audio = blob.read()
    audio_source = AudioSource(audio, False, False)
    print(audio_source.input)
    mycallback = MyRecognizeCallback()
    speech_to_text.recognize_using_websocket(audio=blob,
                                             content_type='audio/webm; codecs=opus',
                                             recognize_callback=mycallback,
                                             model='pt-BR_NarrowbandModel',
                                             interim_results=False)
from flask import Flask, escape, render_template, request
from flask_socketio import SocketIO
from dictation import start_stream
from reading import start_reading
import time

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('audioMessage')
def handle_message(audioMessage):
    print(audioMessage)

@app.route('/')
def index():
	return render_template('ouvir.html')

@app.route('/apresentar')
def resposta():
    iteracoes = request.args['iteracoes']
    print(f"em resposta {type(iteracoes)}")
    iter = int(iteracoes)
    return render_template('apresentacao.html', iter=iter)

@app.route('/ouvir')
def ouvir():

    print('chegou em ouvir')
    return render_template('ouvir.html')


@app.route('/interpretar', methods= ['GET','POST'])
def interpretar():

    data = request.data
    print(type(data))
    print('chegou em interpretar')
    return 'interpretado!!!!'


@app.route('/<name>')
def hello(name):
	return f'hello {escape(name)}!'

if __name__ == "__main__":
    socketio.run(app)
    #app.run(host="127.0.0.1", port="5000", debug=True)
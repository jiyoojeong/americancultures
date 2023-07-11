from flask import Flask, render_template
from flask_socketio import SocketIo, send, emit
import datetime as dt

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@socketio.on('my event') #decorator to catch an event called my event
def test_message(message):
    emit('my resp', {'data': 'got it'})


@app.route("/senate")
def senate():
    now = dt.datetime.now()
    date = now.strftime("%m/%d/%Y %H:%M:%S")
    # do your things here
    return "Last Senate Update: " + date


@app.route("/classes")
def classes():
    now = dt.datetime.now()
    date = now.strftime("%m/%d/%Y %H:%M:%S")
    # do your things here
    return "Last Classes Update: " + date
    # return "It works!"


if __name__ == "__main__":
    socketio.run(app)

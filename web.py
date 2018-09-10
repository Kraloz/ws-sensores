# -*- coding: utf-8 -*-

# -Librería de eventos-
import eventlet
eventlet.monkey_patch()
# ---------------------
#   -Webserver-
from flask import Flask, render_template, jsonify
# ---------------------
# -Extensión para flask de la SocketIO APi-
from flask_socketio import SocketIO, emit
# ---------------------
#  -Para variables de entorno-
from os import environ
from dotenv import load_dotenv, find_dotenv
# ---------------------
from models import db, ma, Sensor, SensorSchema


__author__ = "Tomás Aprile"


# Traigo las variables de entorno
load_dotenv(find_dotenv())
# Instancio para el modelo
app = Flask(__name__)


# Settings
app.config['SECRET_KEY'] =  environ.get('SECRET_KEY')
app.config['DEBUG'] = True if environ.get('DEBUG') == 'True' else False

# BD
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#socketIO
DOMAIN = environ.get('DOMAIN')
ASYNC_MODE = environ.get('ASYNC_MODE')
socketio = SocketIO(app, async_mode=ASYNC_MODE)


""" Enrutamiento
"""
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/edit")
def edit():
    return render_template("edit.html", title="Edición", nombre="pai")

@app.route("/json")
def json():
    return render_template("json.html", title="json", nombre="pai")


""" Listeners """
@socketio.on("connect")
def test_connect():
    print("Client connected!")


@socketio.on("selectAll")
def handle_selectAll():
    """ Returns ALL the sensors from the db """
    sensor = Sensor.query.all()
    
    sensor_schema = SensorSchema(many=True)

    output = sensor_schema.dump(sensor).data

    socketio.emit("respuestaSensores", {"sensores": output})

@socketio.on("updateValue")
def test_connect(json_data):
    #Defino el esquema
    schema = SensorSchema()
    # deserializo el json a mi esquema
    json_deseria = schema.loads(json_data, partial=True)
    # lo parseo a un obj de mi modelo
    obj_json = json_deseria.data
    # traigo un sensor
    sensor = Sensor.query.get(1)
    # cambio el valor del sensor por el valor que me llegó del json
    sensor.valor = obj_json.valor
    # commiteo los cambios
    db.session.commit()   
    # llamo a la función que le actualiza los datos a los clientes 
    handle_selectAll()


# Inicializamos el servidor
if __name__ == '__main__':   
    socketio.run(app)

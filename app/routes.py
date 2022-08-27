import os
import socket
from flask import send_from_directory, jsonify, request, render_template
from app import app
import datetime
from app import thermo


@app.route('/')
@app.route('/index')
def index():
    hostname = socket.gethostname()
    when = datetime.datetime.now()
    temperature = format(round(thermo.read_temp()[0], 3), 'f')
    return render_template('index.html', title='ThermoService', hostname=hostname, when=when, temperature=temperature)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/logo.svg')
def logo():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(os.path.join(app.root_path, '../static'), 'favicon.svg', mimetype='image/svg+xml')


@app.route('/celsius', methods=['GET'])
def ReturnJSON():
    # print(' C=%3.3f  F=%3.3f' % read_temp())
    if (request.method == 'GET'):
        data = {
            "rom": thermo.read_rom(),
            "time": datetime.datetime.now(),
            "sensor": socket.gethostname(),
            "temperature": thermo.read_temp()[0]
        }

        return jsonify(data)

import os
import socket
from flask import send_from_directory, jsonify, request
from app import app
import datetime
import glob
import time

@app.route('/')
@app.route('/index')
def index():
    server = {'hostname': socket.gethostname()}
    return '''
<html>
    <head>
        <title>ThermoService</title>
    </head>
    <body>
        <img src="/logo.svg" title="ThermoService logo" style="width: 20%">
        <h1>Thermoservice on, ''' + server['hostname'] + '''!</h1>
        <a href="/celsius">Celsius Temperature Endpoint</a>
    </body>
</html>'''


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/logo.svg')
def logo():
    print(os.path.join(app.root_path, 'static'))
    return send_from_directory(os.path.join(app.root_path, '../static'), 'favicon.svg', mimetype='image/svg+xml')


@app.route('/celsius', methods=['GET'])
def ReturnJSON():
    if (request.method == 'GET'):
        data = {
            "time": datetime.datetime.now(),
            "sensor": socket.gethostname(),
            "temperature": 32.4
        }

        return jsonify(data)

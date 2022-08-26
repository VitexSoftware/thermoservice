import os
import socket
from flask import send_from_directory, jsonify, request
from app import app
import datetime
from app import thermo


@app.route('/')
@app.route('/index')
def index():
    server = {'hostname': socket.gethostname(), 'celsius': format( round(thermo.read_temp()[0],3), 'f')}
    return '''
<html>
    <head>
        <title>ThermoService</title>
        <style>
$t: rgba(255, 0, 0, 0);
$w: rgba(255, 255, 255, 0.98);

* {
  box-sizing: border-box;
}

.sticker {
  --c1: #ef548f;
  --c2: #ef8b6d;
  --c3: #cfef6b;
  --c4: #3bf0c1;
  --c5: #bb4af0;
  --shine-angle: 15deg;
  display: inline-grid;
  grid-template-areas: "text";
  place-items: center;
  font-family: "Alegreya Sans SC", sans-serif;
  font-weight: 900;
  font-style: italic;
  font-size: clamp(3rem, 15vw, 10rem);
  text-transform: uppercase;
  color: var(--c5);

  &-lg {
    font-size: clamp(6rem, 30vw, 20rem);
  }

  span {
    background: linear-gradient(
        var(--shine-angle),
        $t 0%,
        $t 35%,
        $w 49.95%,
        $w 50.15%,
        $t 65%,
        $t
      ),
      linear-gradient(
        to right,
        var(--c1),
        var(--c2),
        var(--c3),
        var(--c4),
        var(--c5)
      );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    -webkit-text-stroke: 0.01em rgba(0, 0, 0, 0.6);
    // FUn fact - letter-spacing messes with the ability of the
    // gradient to cover all the text :(
  }

  & > *,
  &::before,
  &::after {
    grid-area: text;
  }

  &::before,
  &::after {
    content: attr(data-text);
    color: #fff;
  }

  &::before {
    -webkit-text-stroke: 0.21em white;
    background: no-repeat linear-gradient(white, white) 15% 50% / 85% 60%;

    // Original failed attempt
    // letter-spacing: -0.04em;
    // transform: scale(1.12) translateX(-0.02em) translateY(0.002em);
    // text-shadow: 0.002em 0.002em 0.02em rgba(0, 0, 0, 0.75);
    // -webkit-text-stroke: 0.001em rgba(0, 0, 0, 0.6);
  }

  &::after {
    text-shadow: 0.07em 0.08em 0.05em rgba(0, 0, 0, 0.75),
      -0.07em -0.05em 0.05em rgba(0, 0, 0, 0.75);
    z-index: -2;
  }
}

body {
  min-height: 100vh;
  min-height: -webkit-fill-available;
  display: grid;
  place-content: center;
  font-family: sans-serif;
  background-color: #d1dbe8;
  line-height: 1;
  color: var(--c5);
}
        
        </style>
    </head>
    <body>
        <img src="/logo.svg" title="ThermoService logo" style="width: 20%">
        <h1>Thermoservice on, ''' + server['hostname'] + '''!</h1>
        <span class="sticker sticker-lg" data-text="''' + server['celsius'] + '''&deg;"><span>''' + server['celsius'] + '''&deg;</span></span>
        <div><a href="/celsius">Celsius Temperature Endpoint</a></div>
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
    # print(' C=%3.3f  F=%3.3f' % read_temp())
    if (request.method == 'GET'):
        data = {
            "rom": thermo.read_rom(),
            "time": datetime.datetime.now(),
            "sensor": socket.gethostname(),
            "temperature": thermo.read_temp()[0]
        }

        return jsonify(data)

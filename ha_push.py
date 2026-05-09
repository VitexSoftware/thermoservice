#!/usr/bin/env python3
"""Push DS18B20 temperature to Home Assistant REST API.

Environment variables:
  HASS_URL    - Home Assistant base URL (default: http://localhost:8123)
  HASS_TOKEN  - Long-lived access token
"""

import os
import socket
import sys

# Support both installed location and running from project root
sys.path.insert(0, '/usr/share/thermoservice/app')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

import requests
from thermo import read_rom, read_temp

HASS_URL = os.environ.get('HASS_URL', 'http://localhost:8123').rstrip('/')
HASS_TOKEN = os.environ.get('HASS_TOKEN', '')
ENTITY_ID = 'sensor.thermoservice_temperature'


def push_temperature():
    temp_c, _ = read_temp()
    if temp_c is None:
        print('No DS18B20 sensor found or unable to read temperature.', file=sys.stderr)
        sys.exit(1)

    rom = (read_rom() or '').strip()
    hostname = socket.gethostname()

    payload = {
        'state': str(round(temp_c, 3)),
        'attributes': {
            'unit_of_measurement': '\u00b0C',
            'device_class': 'temperature',
            'state_class': 'measurement',
            'friendly_name': f'Thermoservice {hostname}',
            'rom': rom,
            'sensor': hostname,
        },
    }

    url = f'{HASS_URL}/api/states/{ENTITY_ID}'
    headers = {
        'Authorization': f'Bearer {HASS_TOKEN}',
        'Content-Type': 'application/json',
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    print(f'Pushed {temp_c}\u00b0C to {url}')


if __name__ == '__main__':
    push_temperature()

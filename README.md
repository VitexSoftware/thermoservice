# thermoservice

Temperature sharing service for DS18B20

![Pi Thermo Service](static/favicon.svg?raw=true)

## Installation

### Debian / Ubuntu

```bash
sudo curl -fsSL http://repo.vitexsoftware.com/KEY.gpg -o /usr/share/keyrings/vitexsoftware-archive-keyring.gpg && \
echo "Types: deb
URIs: http://repo.vitexsoftware.com/
Suites: $(lsb_release -sc)
Components: main
Signed-By: /usr/share/keyrings/vitexsoftware-archive-keyring.gpg" | sudo tee /etc/apt/sources.list.d/vitexsoftware.sources

sudo apt update
sudo apt install thermoservice
```

## Usage

Run command `thermo` to print current temperature to stdout:

```bash
$ thermo
23.125
```

The service automatically starts and exposes a web interface on port 5000, displaying the current temperature from the DS18B20 sensor.

## Description

Thermoservice is a lightweight Flask-based web service designed for Raspberry Pi and similar devices equipped with DS18B20 temperature sensors. It reads temperature data from the 1-Wire interface and provides both a command-line tool and a web interface for monitoring temperature readings.

**Features:**
- Simple command-line temperature reading with `thermo` command
- Web interface on port 5000 for real-time temperature display
- Systemd service integration for automatic startup
- Designed for DS18B20 digital temperature sensors
- Graceful handling when no sensor hardware is detected

**Requirements:**
- DS18B20 temperature sensor connected via 1-Wire interface
- Raspberry Pi or compatible device with 1-Wire support enabled

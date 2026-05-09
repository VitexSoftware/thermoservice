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

### Zabbix Integration

To enable Zabbix monitoring of temperature sensors:

```bash
sudo apt install thermometer-zabbix
```

This installs Zabbix Agent configuration that provides the following user parameters:
- `sensor.temp.value` - Current temperature in Celsius
- `sensor.temp.celsius` - Current temperature in Celsius

The Zabbix agent will automatically restart after installation to load the new configuration.

**Zabbix Template:**

A pre-configured Zabbix 7.4 template is available in the repository at `zabbix_template_thermoservice.yaml`. Import this template into your Zabbix server to automatically configure:
- Temperature monitoring items
- Threshold triggers (high temperature, freezing, no data alerts)
- Temperature trend graphs

To use the template:
1. Import `zabbix_template_thermoservice.yaml` into Zabbix
2. Assign the "DS18B20 Temperature Sensor" template to your host
3. Temperature data will be collected automatically

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
- Web interface on port 5000 for real-time temperature display with cyberpunk futuristic design
- Systemd service integration for automatic startup
- Designed for DS18B20 digital temperature sensors
- Graceful handling when no sensor hardware is detected
- Optional Zabbix Agent integration for monitoring (thermometer-zabbix package)
- Pre-configured Zabbix 7.4 template with triggers and graphs

**Requirements:**

- DS18B20 temperature sensor connected via 1-Wire interface
- Raspberry Pi or compatible device with 1-Wire support enabled

**AppStream / Icon:**

The SVG icon (`static/favicon.svg`) is installed as
`/usr/share/icons/hicolor/scalable/apps/com.vitexsoftware.thermoservice.svg`
and referenced by the AppStream metainfo file
`com.vitexsoftware.thermoservice.metainfo.xml`.

## Man Pages

After installation the following manual pages are available:

- `man 1 thermo` – CLI command reference
- `man 8 thermoservice` – Service / HTTP API reference
- `man 8 ha_push` – Home Assistant push script reference

## Testing

Unit tests use `pytest` and require `python3-flask` and `python3-requests`.
No real sensor hardware is needed — the tests mock all 1-Wire filesystem access.

```bash
python3 -m pytest tests/ -v
```

## Home Assistant Integration

Two approaches are supported:

### Option A: Pull (HA RESTful Sensor)

Add the following to your Home Assistant `configuration.yaml` to have HA poll the thermoservice endpoint every 60 seconds:

```yaml
sensor:
  - platform: rest
    name: "Thermoservice Temperature"
    resource: http://thermometer.local:5000/celsius
    value_template: "{{ value_json.temperature }}"
    unit_of_measurement: "°C"
    device_class: temperature
    state_class: measurement
    scan_interval: 60
    json_attributes:
      - rom
      - sensor
      - time
```

Replace `thermometer.local` with your thermoservice host.

### Option B: Push (`thermoservice-homeassistant` package)

Install the push package on the thermoservice device:

```bash
sudo apt install thermoservice-homeassistant
```

Configure your HA instance in `/etc/default/thermoservice-homeassistant`:

```bash
HASS_URL=http://homeassistant.local:8123
HASS_TOKEN=your-long-lived-access-token
```

Generate a long-lived access token in HA under **Profile → Security → Long-Lived Access Tokens**.

Enable and start the systemd timer:

```bash
sudo systemctl enable --now thermoservice-homeassistant.timer
```

The timer runs `ha_push.py` every 60 seconds, creating/updating the entity `sensor.thermoservice_temperature` in Home Assistant.

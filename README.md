# thermoservice

Temperature sharing service for DS18B20

![Pi Thermo Service](static/favicon.svg?raw=true)

ExecStartPre=modprobe w1-gpio
ExecStartPre=modprobe w1-therm

https://www.abelectronics.co.uk/kb/article/1096/using-the-1-wire-w1-subsystem-with-the-1-wire-pi
https://www.abelectronics.co.uk/kb/article/1/i2c-part-2---enabling-i-c-on-the-raspberry-pi

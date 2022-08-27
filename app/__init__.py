import os
import sys
from flask import Flask

path = '/sys/bus/w1/devices/'
if not os.path.exists(path):
    sys.stderr.write('The /sys/bus/w1/devices not exists. Is GPIO enabled ?\n')

app = Flask(__name__)

from app import routes

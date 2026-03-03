import glob
import time

base_dir = '/sys/bus/w1/devices/'
# Get all the filenames begin with 28 in the path base_dir.
devices = glob.glob(base_dir + '28*')
if not devices:
    device_folder = None
    device_file = None
else:
    device_folder = devices[0]
    device_file = device_folder + '/w1_slave'


def read_rom():
    if device_folder is None:
        return None
    name_file = device_folder+'/name'
    try:
        f = open(name_file, 'r')
        return f.readline()
    except (IOError, OSError):
        return None


def read_temp_raw():
    if device_file is None:
        return None
    try:
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    except (IOError, OSError):
        return None


def read_temp():
    lines = read_temp_raw()
    if lines is None:
        return None, None
    # Analyze if the last 3 characters are 'YES'.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
        if lines is None:
            return None, None
    # Find the index of 't=' in a string.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        # Read the temperature .
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
    return None, None

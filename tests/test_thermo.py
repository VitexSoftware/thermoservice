"""Tests for app/thermo.py sensor reading functions."""
import sys
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Ensure the project root is on the path so 'app' is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Patch glob.glob at import time so the module-level device detection
# does not depend on real hardware.
_FAKE_DEVICE = '/sys/bus/w1/devices/28-fakerom'
_FAKE_W1_SLAVE = (
    '50 01 4b 46 7f ff 0c 10 1c : crc=1c YES\n'
    '50 01 4b 46 7f ff 0c 10 1c t=21312\n'
)
_FAKE_NAME = '28-fakerom\n'

with patch('glob.glob', return_value=[_FAKE_DEVICE]):
    import app.thermo as thermo


class TestReadRom(unittest.TestCase):
    def test_no_sensor_returns_none(self):
        original = thermo.device_folder
        thermo.device_folder = None
        try:
            self.assertIsNone(thermo.read_rom())
        finally:
            thermo.device_folder = original

    def test_returns_sensor_name(self):
        thermo.device_folder = _FAKE_DEVICE
        with patch('builtins.open', mock_open(read_data=_FAKE_NAME)):
            result = thermo.read_rom()
        self.assertEqual(result, _FAKE_NAME)

    def test_io_error_returns_none(self):
        thermo.device_folder = _FAKE_DEVICE
        with patch('builtins.open', side_effect=IOError('no device')):
            result = thermo.read_rom()
        self.assertIsNone(result)


class TestReadTempRaw(unittest.TestCase):
    def test_no_sensor_returns_none(self):
        original = thermo.device_file
        thermo.device_file = None
        try:
            self.assertIsNone(thermo.read_temp_raw())
        finally:
            thermo.device_file = original

    def test_returns_lines(self):
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', mock_open(read_data=_FAKE_W1_SLAVE)):
            lines = thermo.read_temp_raw()
        self.assertEqual(len(lines), 2)
        self.assertIn('YES', lines[0])
        self.assertIn('t=', lines[1])

    def test_io_error_returns_none(self):
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', side_effect=OSError('no device')):
            self.assertIsNone(thermo.read_temp_raw())


class TestReadTemp(unittest.TestCase):
    def test_no_sensor_returns_none_tuple(self):
        original = thermo.device_file
        thermo.device_file = None
        try:
            temp_c, temp_f = thermo.read_temp()
            self.assertIsNone(temp_c)
            self.assertIsNone(temp_f)
        finally:
            thermo.device_file = original

    def test_valid_reading_celsius(self):
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', mock_open(read_data=_FAKE_W1_SLAVE)):
            temp_c, temp_f = thermo.read_temp()
        # 21312 / 1000.0 = 21.312
        self.assertAlmostEqual(temp_c, 21.312, places=3)

    def test_valid_reading_fahrenheit(self):
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', mock_open(read_data=_FAKE_W1_SLAVE)):
            temp_c, temp_f = thermo.read_temp()
        expected_f = 21.312 * 9.0 / 5.0 + 32.0
        self.assertAlmostEqual(temp_f, expected_f, places=3)

    def test_zero_celsius(self):
        w1_data = (
            'aa bb : crc=xx YES\n'
            'aa bb t=0\n'
        )
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', mock_open(read_data=w1_data)):
            temp_c, temp_f = thermo.read_temp()
        self.assertAlmostEqual(temp_c, 0.0, places=3)
        self.assertAlmostEqual(temp_f, 32.0, places=3)

    def test_negative_temperature(self):
        w1_data = (
            'aa bb : crc=xx YES\n'
            'aa bb t=-5000\n'
        )
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', mock_open(read_data=w1_data)):
            temp_c, temp_f = thermo.read_temp()
        self.assertAlmostEqual(temp_c, -5.0, places=3)

    def test_io_error_returns_none_tuple(self):
        thermo.device_file = _FAKE_DEVICE + '/w1_slave'
        with patch('builtins.open', side_effect=IOError):
            temp_c, temp_f = thermo.read_temp()
        self.assertIsNone(temp_c)
        self.assertIsNone(temp_f)


if __name__ == '__main__':
    unittest.main()

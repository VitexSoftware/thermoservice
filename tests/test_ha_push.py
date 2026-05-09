"""Tests for ha_push.py – Home Assistant temperature push script."""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ha_push.py inserts paths at import time; ensure app.thermo is importable
# by faking the sensor glob before any import of app.thermo.
with patch('glob.glob', return_value=['/sys/bus/w1/devices/28-fakerom']):
    import ha_push


class TestPushTemperature(unittest.TestCase):
    def _make_ok_response(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    def test_push_success(self):
        with patch('ha_push.read_temp', return_value=(21.312, 70.362)), \
             patch('ha_push.read_rom', return_value='28-fakerom'), \
             patch('requests.post', return_value=self._make_ok_response()) as mock_post, \
             patch.dict(os.environ, {'HASS_URL': 'http://ha.local:8123',
                                     'HASS_TOKEN': 'fake-token'}):
            # Re-evaluate module-level constants
            ha_push.HASS_URL = os.environ['HASS_URL'].rstrip('/')
            ha_push.HASS_TOKEN = os.environ['HASS_TOKEN']
            ha_push.push_temperature()

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get('url', call_kwargs[0][0])
        # URL should contain the entity id
        self.assertIn('sensor.thermoservice_temperature', mock_post.call_args[0][0])

    def test_payload_state_is_rounded(self):
        captured = {}

        def fake_post(url, json=None, headers=None, timeout=None):
            captured['payload'] = json
            return self._make_ok_response()

        with patch('ha_push.read_temp', return_value=(21.3124567, 70.362)), \
             patch('ha_push.read_rom', return_value='28-fakerom'), \
             patch('requests.post', side_effect=fake_post):
            ha_push.push_temperature()

        self.assertIn('payload', captured)
        state_val = float(captured['payload']['state'])
        self.assertAlmostEqual(state_val, 21.312, places=3)

    def test_payload_attributes(self):
        captured = {}

        def fake_post(url, json=None, headers=None, timeout=None):
            captured['payload'] = json
            return self._make_ok_response()

        with patch('ha_push.read_temp', return_value=(21.312, 70.362)), \
             patch('ha_push.read_rom', return_value='28-fakerom'), \
             patch('requests.post', side_effect=fake_post):
            ha_push.push_temperature()

        attrs = captured['payload']['attributes']
        self.assertEqual(attrs['unit_of_measurement'], '°C')
        self.assertEqual(attrs['device_class'], 'temperature')
        self.assertEqual(attrs['state_class'], 'measurement')
        self.assertIn('rom', attrs)
        self.assertIn('sensor', attrs)
        self.assertIn('friendly_name', attrs)

    def test_no_sensor_exits_with_error(self):
        with patch('ha_push.read_temp', return_value=(None, None)):
            with self.assertRaises(SystemExit) as cm:
                ha_push.push_temperature()
        self.assertEqual(cm.exception.code, 1)

    def test_http_error_propagates(self):
        import requests

        def bad_post(*args, **kwargs):
            r = MagicMock()
            r.raise_for_status.side_effect = requests.exceptions.HTTPError('403')
            return r

        with patch('ha_push.read_temp', return_value=(21.312, 70.362)), \
             patch('ha_push.read_rom', return_value='28-fakerom'), \
             patch('requests.post', side_effect=bad_post):
            with self.assertRaises(Exception):
                ha_push.push_temperature()

    def test_bearer_token_in_header(self):
        captured = {}

        def fake_post(url, json=None, headers=None, timeout=None):
            captured['headers'] = headers
            return self._make_ok_response()

        ha_push.HASS_TOKEN = 'super-secret-token'
        with patch('ha_push.read_temp', return_value=(21.312, 70.362)), \
             patch('ha_push.read_rom', return_value='28-fakerom'), \
             patch('requests.post', side_effect=fake_post):
            ha_push.push_temperature()

        self.assertIn('Authorization', captured['headers'])
        self.assertIn('super-secret-token', captured['headers']['Authorization'])


if __name__ == '__main__':
    unittest.main()

"""Tests for Flask routes defined in app/routes.py."""
import sys
import os
import json
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Suppress the missing 1-Wire path warning during import
with patch('os.path.exists', return_value=True), \
     patch('glob.glob', return_value=['/sys/bus/w1/devices/28-fakerom']):
    from app import app as flask_app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        flask_app.config['TESTING'] = True
        self.client = flask_app.test_client()

    # ------------------------------------------------------------------
    # GET /
    # ------------------------------------------------------------------
    def test_index_with_sensor(self):
        with patch('app.thermo.read_temp', return_value=(21.312, 70.362)):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        body = response.data.decode()
        self.assertIn('21.312000', body)

    def test_index_no_sensor(self):
        with patch('app.thermo.read_temp', return_value=(None, None)):
            response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        body = response.data.decode()
        self.assertIn('No DS18B20 sensor detected', body)

    def test_index_alias(self):
        with patch('app.thermo.read_temp', return_value=(None, None)):
            response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # GET /celsius
    # ------------------------------------------------------------------
    def test_celsius_with_sensor(self):
        with patch('app.thermo.read_temp', return_value=(21.312, 70.362)), \
             patch('app.thermo.read_rom', return_value='28-fakerom\n'):
            response = self.client.get('/celsius')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertAlmostEqual(data['temperature'], 21.312, places=3)
        self.assertIn('rom', data)
        self.assertIn('sensor', data)
        self.assertIn('time', data)
        self.assertNotIn('error', data)

    def test_celsius_no_sensor(self):
        with patch('app.thermo.read_temp', return_value=(None, None)), \
             patch('app.thermo.read_rom', return_value=None):
            response = self.client.get('/celsius')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsNone(data['temperature'])
        self.assertIn('error', data)
        self.assertIn('No DS18B20', data['error'])

    # ------------------------------------------------------------------
    # Static assets
    # ------------------------------------------------------------------
    def test_favicon_ico(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', response.content_type)

    def test_logo_svg(self):
        response = self.client.get('/logo.svg')
        self.assertEqual(response.status_code, 200)
        self.assertIn('svg', response.content_type)


if __name__ == '__main__':
    unittest.main()

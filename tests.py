import asyncio
import unittest
from unittest.mock import patch
from config import HOST, PORT
from main import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_enable_channel(self):
        data = {'channel': 1, 'voltage': 12.0, 'current': 2.0}
        with patch('scpi.enable_channel') as mock_enable_channel:
            mock_enable_channel.return_value = asyncio.Future()
            mock_enable_channel.return_value.set_result(None)
            response = self.app.post('/enable', json=data)
            mock_enable_channel.assert_called_once_with(HOST, PORT, 1, 12.0, 2.0)
            self.assertEqual(response.status_code, 200)

    def test_disable_channel(self):
        # Аналогично
        pass

    def test_get_channel_status(self):
        # Аналогично
        pass


if __name__ == '__main':
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import asyncio
import json

from scpi import send_scpi_command, set_channel_voltage_and_current, \
    enable_channel_output, disable_channel_output, poll_channel_status, \
    enable_channel, disable_channel, get_channel_status, poll_telemetry


class TestScpi(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        self.loop.close()

    def test_send_scpi_command(self):
        host = "dummy_host"
        port = 12345
        command = "dummy_command"

        async def mock_open_connection(*args, **kwargs):
            reader = MagicMock()
            writer = MagicMock()
            writer.write.return_value = None
            writer.drain.return_value = None
            reader.readuntil.return_value = b"response\n"
            reader.decode.return_value = "response"
            return reader, writer

        with patch("asyncio.open_connection",
                   side_effect=mock_open_connection):
            result = self.loop.run_until_complete(send_scpi_command(host,
                                                                    port,
                                                                    command))

        self.assertEqual(result, "response")

    def test_set_channel_voltage_and_current(self):
        host = "dummy_host"
        port = 12345
        channel = 1
        voltage = 10.0
        current = 2.0

        send_scpi_command_mock = MagicMock(side_effect=[None, None])

        with patch("scpi.send_scpi_command", send_scpi_command_mock):
            self.loop.run_until_complete(set_channel_voltage_and_current(
                host,
                port,
                channel,
                voltage,
                current))
        send_scpi_command_mock.assert_any_call(
            host,
            port,
            f'SOURCE:CHANNEL{channel}:VOLTAGE {voltage}')
        send_scpi_command_mock.assert_any_call(
            host,
            port,
            f'SOURCE:CHANNEL{channel}:CURRENT {current}')

    def test_enable_channel_output(self):
        host = "dummy_host"
        port = 12345
        channel = 1

        send_scpi_command_mock = MagicMock()

        with patch("scpi.send_scpi_command", send_scpi_command_mock):
            self.loop.run_until_complete(enable_channel_output(host, port,
                                                               channel))

        send_scpi_command_mock.assert_called_once_with(
            host,
            port,
            f'OUTPUT:CHANNEL{channel}:STATE ON')

    def test_disable_channel_output(self):
        host = "dummy_host"
        port = 12345
        channel = 1

        send_scpi_command_mock = MagicMock()

        with patch("scpi.send_scpi_command", send_scpi_command_mock):
            self.loop.run_until_complete(disable_channel_output(host, port,
                                                                channel))

        send_scpi_command_mock.assert_called_once_with(
            host,
            port,
            f'OUTPUT:CHANNEL{channel}:STATE OFF')

    def test_poll_channel_status(self):
        host = "dummy_host"
        port = 12345
        channel = 1

        async def send_scpi_command_mock(host, port, command):
            if command == f'MEASURE:CHANNEL{channel}:VOLTAGE?':
                return "10.0"
            elif command == f'MEASURE:CHANNEL{channel}:CURRENT?':
                return "2.0"

        with patch("scpi.send_scpi_command",
                   side_effect=send_scpi_command_mock):
            result = self.loop.run_until_complete(poll_channel_status(host,
                                                                      port,
                                                                      channel))

        self.assertEqual(result, {'voltage': "10.0", 'current': "2.0"})

    def test_enable_channel(self):
        host = "dummy_host"
        port = 12345
        channel = 1
        voltage = 10.0
        current = 2.0

        set_channel_voltage_and_current_mock = MagicMock()
        enable_channel_output_mock = MagicMock()

        with patch("scpi.set_channel_voltage_and_current",
                   set_channel_voltage_and_current_mock):
            with patch("scpi.enable_channel_output",
                       enable_channel_output_mock):
                self.loop.run_until_complete(enable_channel(
                    host,
                    port,
                    channel,
                    voltage,
                    current))

        set_channel_voltage_and_current_mock.assert_called_once_with(
            host,
            port,
            channel,
            voltage,
            current)
        enable_channel_output_mock.assert_called_once_with(host, port, channel)

    def test_disable_channel(self):
        host = "dummy_host"
        port = 12345
        channel = 1

        disable_channel_output_mock = MagicMock()

        with patch("scpi.disable_channel_output",
                   disable_channel_output_mock):
            self.loop.run_until_complete(disable_channel(host, port, channel))

        disable_channel_output_mock.assert_called_once_with(host, port,
                                                            channel)

    def test_get_channel_status(self):
        host = "dummy_host"
        port = 12345

        async def poll_channel_status_mock(host, port, channel):
            if channel == 1:
                return {'voltage': "10.0", 'current': "2.0"}
            elif channel == 2:
                return {'voltage': "15.0", 'current': "3.0"}

        with patch("scpi.poll_channel_status",
                   side_effect=poll_channel_status_mock):
            result = self.loop.run_until_complete(get_channel_status(host,
                                                                     port))

        expected_result = {
            'Channel1': {'voltage': "10.0", 'current': "2.0"},
            'Channel2': {'voltage': "15.0", 'current': "3.0"},
            'Channel3': {'voltage': "0.0", 'current': "0.0"},
            'Channel4': {'voltage': "0.0", 'current': "0.0"}
        }
        self.assertEqual(result, json.dumps(expected_result))

    def test_poll_telemetry(self):
        host = "dummy_host"
        port = 12345

        async def send_scpi_command_mock(host, port, command):
            if command == 'MEASURE:VOLTAGE?':
                return "10.0"
            elif command == 'MEASURE:CURRENT?':
                return "2.0"
            elif command == 'MEASURE:POWER?':
                return "20.0"

        with patch("scpi.send_scpi_command",
                   side_effect=send_scpi_command_mock):
            with patch("scpi.log_telemetry"):
                with patch("asyncio.sleep"):
                    self.loop.run_until_complete(poll_telemetry(host, port))

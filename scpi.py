import asyncio
import json
import time
from logger import log_telemetry


async def send_scpi_command(host, port, command):
    """
    Отправляет SCPI-команду на указанный хост и порт и возвращает ответ.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param command: SCPI-команда для отправки.
    :return: Ответ на SCPI-команду.
    """
    reader, writer = await asyncio.open_connection(host, port)
    try:
        writer.write(command.encode() + b'\n')
        await writer.drain()
        data = await reader.readuntil(b'\n')
        return data.decode().strip()
    finally:
        writer.close()
        await writer.wait_closed()


async def set_channel_voltage_and_current(host, port, channel,
                                          voltage, current):
    """
    Устанавливает заданное напряжение и ток на указанном канале.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, на котором устанавливается напряжение и ток.
    :param voltage: Устанавливаемое напряжение.
    :param current: Устанавливаемый ток.
    """
    await send_scpi_command(host,
                            port, f'SOURCE:CHANNEL{channel}:VOLTAGE {voltage}')
    await send_scpi_command(host,
                            port, f'SOURCE:CHANNEL{channel}:CURRENT {current}')


async def enable_channel_output(host, port, channel):
    """
    Включает выход на указанном канале.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, который будет включен.
    """
    await send_scpi_command(host, port, f'OUTPUT:CHANNEL{channel}:STATE ON')


async def disable_channel_output(host, port, channel):
    """
    Выключает выход на указанном канале.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, который будет выключен.
    """
    await send_scpi_command(host, port, f'OUTPUT:CHANNEL{channel}:STATE OFF')


async def poll_channel_status(host, port, channel):
    """
    Запрашивает статус указанного канала.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, статус которого будет запрошен.
    :return: Словарь с данными о напряжении и токе на канале.
    """
    voltage = await send_scpi_command(
        host,
        port,
        f'MEASURE:CHANNEL{channel}:VOLTAGE?')
    current = await send_scpi_command(
        host,
        port,
        f'MEASURE:CHANNEL{channel}:CURRENT?')
    return {'voltage': voltage, 'current': current}


async def enable_channel(host, port, channel, voltage, current):
    """
    Устанавливает заданное напряжение и ток.
    Затем включает выход на указанном канале.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, на котором устанавливается напряжение и ток.
    :param voltage: Устанавливаемое напряжение.
    :param current: Устанавливаемый ток.
    """
    await set_channel_voltage_and_current(host, port, channel,
                                          voltage, current)
    await enable_channel_output(host, port, channel)


async def disable_channel(host, port, channel):
    """
    Выключает выход на указанном канале.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :param channel: Номер канала, который будет выключен.
    """
    await disable_channel_output(host, port, channel)


async def get_channel_status(host, port):
    """
    Запрашивает статус всех каналов.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    :return: JSON-строка с данными о статусе всех каналов.
    """
    channel_data = {}
    for channel in range(1, 5):
        channel_data[f'Channel{channel}'] = await poll_channel_status(
            host,
            port,
            channel)
    return json.dumps(channel_data)


async def poll_telemetry(host, port):
    """
    Запрашивает телеметрию (напряжение, ток, мощность).
    Затем записывает данные в лог.
    :param host: IP-адрес хоста, к которому будет отправлена команда.
    :param port: Порт, через который будет отправлена команда.
    """
    while True:
        voltage = await send_scpi_command(host, port, 'MEASURE:VOLTAGE?')
        current = await send_scpi_command(host, port, 'MEASURE:CURRENT?')
        power = await send_scpi_command(host, port, 'MEASURE:POWER?')

        timestamp = int(time.time())
        telemetry_data = {
            'timestamp': timestamp,
            'voltage': voltage,
            'current': current,
            'power': power
        }
        log_telemetry('telemetry.log', telemetry_data)

        await asyncio.sleep(1)

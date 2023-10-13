from aiohttp import web
from config import HOST, PORT
from scpi import enable_channel, disable_channel, get_channel_status


async def handle_enable(request):
    """
    Обработчик для включения канала.
    Args: request: Объект запроса aiohttp.
    Returns: web.Response: Ответ, сообщающий об успешном включении канала.
    """
    data = await request.json()
    channel = data['channel']
    voltage = data['voltage']
    current = data['current']
    await enable_channel(HOST, PORT, channel, voltage, current)
    return web.Response(text=f'Channel {channel} enabled')


async def handle_disable(request):
    """
    Обработчик для выключения канала.
    Args: request: Объект запроса aiohttp.
    Returns: web.Response: Ответ, сообщающий об успешном выключении канала.
    """
    data = await request.json()
    channel = data['channel']
    await disable_channel(HOST, PORT, channel)
    return web.Response(text=f'Channel {channel} disabled')


async def handle_status(request):
    """
    Обработчик для получения статуса канала.
    Args: request: Объект запроса aiohttp.
    Returns: web.Response: Ответ, содержащий информацию о статусе канала.
    """
    status = await get_channel_status(HOST, PORT)
    return web.Response(text=status)

app = web.Application()
app.router.add_post('/enable', handle_enable)
app.router.add_post('/disable', handle_disable)
app.router.add_get('/status', handle_status)

import asyncio
from aiohttp import web
from api import app
from config import HOST, PORT
from scpi import poll_telemetry


loop = asyncio.get_event_loop()
loop.create_task(poll_telemetry(HOST, PORT))

web.run_app(app)

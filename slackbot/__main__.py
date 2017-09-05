from . import SlackListener
import logging
import asyncio
import time

loop = asyncio.get_event_loop()
logging.basicConfig(level="DEBUG")

listener = SlackListener("")
def dummy1(*args, **kwargs):
	listener.logger.info("Dummy connect")

listener.client.rtm_connect = dummy1

@listener.on_message('message')
async def dummy_handler(listener, message):
	raise Exception("Trying stuff out!")
	listener.logger.debug(f"Message: {message}")

def dummy2(*args, **kwargs):
	time.sleep(1)
	listener.logger.info("Dummy read")
	return [{"type": "message"}]
listener.client.rtm_read = dummy2

l_awaitable = listener.run(loop)
loop.run_until_complete(l_awaitable)
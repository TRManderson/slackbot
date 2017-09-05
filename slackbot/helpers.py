from functools import partial, update_wrapper
import asyncio

async def maybe_await(maybe_awaitable):
	if asyncio.iscoroutine(maybe_awaitable) or hasattr(maybe_awaitable, '__await__'):
		return await maybe_awaitable
	else:
		return maybe_awaitable

class MessageHandler(object):
	def __init__(self, client, fn):
		"""
		@message_handler
		def example(listener, text, user, channel, timestamp):
			pass
		"""
		update_wrapper(self, fn)
		self.fn = fn
		client.on_message('message', self)

	async def __call__(self, listener, message):
		result = self.fn(
			listener,
			message.get('text'),
			message.get('user'),
			message.get('channel'),
			message.get('timestamp'),
		)
		return await maybe_await(result)


message_handler = lambda cl: partial(MessageHandler, client=cl)
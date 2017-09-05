import os
import logging
import asyncio
import concurrent.futures as futures
import slackclient
import collections
from multiprocessing import cpu_count
from functools import wraps, partial
from typing import Optional, Callable, Awaitable, Union, Dict, Any, List

Message = Dict[str, Any]

Handler = Callable[['SlackListener', Message], Union[Awaitable, None]]

class SlackListener(object):
    client: slackclient.SlackClient
    executor: futures.Executor
    logger: logging.Logger
    handlers: Dict[str, Dict[str, Handler]]
    loop: Optional[asyncio.AbstractEventLoop]

    def __init__(self, token, executor=None, logger=None):
        self.client = slackclient.SlackClient(token)
        self.executor = executor or futures.ThreadPoolExecutor(max_workers=cpu_count()*2)
        self.logger = logger or logging.getLogger(type(self).__qualname__)
        self.handlers = collections.defaultdict(dict)
        self.loop = None

    def on_message(self, message_type: str) -> Callable[[Handler], None]:
        """
        Designed to be used as a decorator, example:

        @listener.on_message('message')
        @parse_message
        async def fn(listener, message):
            # handle message
            pass

        """
        return partial(self.register_handler, message_type)

    def register_handler(self, message_type: str, handler: Handler, name=None, is_async=None) -> Handler:
        if name is None:
            name = handler.__name__
        assert name not in self.handlers[message_type]
        if not callable(handler):
            raise ValueError(f"Handler {repr(handler)} must be callable")
        if is_async is None:
            # if it's not a coroutine, assume it's a sync function
            is_async = asyncio.iscoroutinefunction(handler)
        if not is_async:
            handler = partial(self._run_in_executor, handler)
        self.handlers[message_type][name] = handler
        return handler

    def _run_in_executor(self, fn: Callable, *args, **kwargs) -> Awaitable:
        """ Run a function in an event loop to get an awaitable"""
        return self.loop.run_in_executor(self.executor, partial(fn, *args, **kwargs))

    async def _await_error(self, name, awaitable):
        try:
            return (await awaitable)
        except:
            self.logger.exception(f'Error in handler "{name}"')
            return None

    async def perform_single_read(self):
        rtm_data = await self.loop.run_in_executor(self.executor, self.client.rtm_read)
        for message in rtm_data:
            if "type" not in message:
                self.logger.error(f"No type in message: {message}")
            handlers = self.handlers[message['type']]
            awaitables = {}
            for name, handler in handlers.items():
                awaitables[name] = self._await_error(name, handler(self, message))
            await asyncio.gather(*awaitables.values(), return_exceptions=True)

    async def run(self, event_loop: asyncio.AbstractEventLoop, connect_with_team_state=True):
        self.loop = event_loop
        self.client.rtm_connect(connect_with_team_state)
        while True:
            try:
                await self.perform_single_read()
            except futures.CancelledError:
                break
        self.loop = None
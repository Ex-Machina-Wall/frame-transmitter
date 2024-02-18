import websockets
from time import sleep
import asyncio
from threading import Thread
import logging
from typing import Union


class WebsocketTransmitter:
    def __init__(self, destination_uri: str):
        self.destination_uri = destination_uri
        self.logger = logging.getLogger(self.__class__.__name__)
        self._data_frame: Union[bytes, None] = b""
        self._running = False
        self._thread: Union[Thread, None] = None

    def start(self):
        self._running = True
        self._thread = Thread(target=self._websocket_thread)
        self._thread.start()

    def stop(self):
        self._running = False
        if not self._thread:
            self.logger.error(
                "self._thread was None when we "
                "expected to see a Thread object")
            return
        try:
            self._thread.join(timeout=5)
        except TimeoutError:
            self.logger.critical(
                "Websocket thread did not stop in less than 5 seconds"
            )

    def set_latest_bytes(self, data_frame: bytes):
        self._data_frame = data_frame

    def _websocket_thread(self):
        while self._running:
            self.logger.debug("Starting websocket task")
            asyncio.run(self._websocket_task())
            self.logger.warning("Websocket task died")
            sleep(1)

    async def _websocket_task(self):
        async with websockets.connect(uri=self.destination_uri) as websocket:
            logger = logging.getLogger(self.__class__.__name__)
            logger.info("Started new websocket")
            while True:
                try:
                    if self._data_frame:
                        await websocket.send(self._data_frame)
                        self._data_frame = None
                    await asyncio.sleep(1 / 40)
                except Exception as e:
                    logging.getLogger(self.__class__.__name__).error(e)
                    await asyncio.sleep(2)
                    break
                if not self._running:
                    return

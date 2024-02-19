import struct
import time

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
        self.duration = 0

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
            self.logger.debug("Websocket task ended")
            sleep(1)

    async def _websocket_task(self):
        # 1 year in seconds
        ping_interval = 60*24*365
        async with websockets.connect(uri=self.destination_uri, ping_interval=ping_interval) as websocket:
            value = await websocket.recv()
            print(value)
            logger = logging.getLogger(self.__class__.__name__)
            logger.info("Started new websocket")
            while True:
                try:
                    if self._data_frame:
                        old_time = time.perf_counter()
                        await websocket.send(self._data_frame)
                        value = await websocket.recv()
                        new_time = time.perf_counter()
                        this_duration = new_time - old_time
                        self.duration = self.duration * 0.9 + (this_duration * 0.1)
                        # value = struct.unpack('B', value)[0]
                        # logger.debug(f"Hand Shake received from server: {value}")
                        logger.critical(f"This duration: {this_duration} | Average duration: {self.duration}")
                        # print(await websocket.recv())
                        self._data_frame = None
                    await asyncio.sleep(0)
                except Exception as e:
                    logging.getLogger(self.__class__.__name__).error(e)
                    await asyncio.sleep(2)
                    break
                if not self._running:
                    return


def main():
    from decouple import config
    import struct
    logging.basicConfig(level=logging.DEBUG)
    transmitter = WebsocketTransmitter(destination_uri=config("DESTINATION_URI"))
    transmitter.start()
    while True:
        for i in range(255):
            # Pack int i into an uint_8 struct
            transmitter.set_latest_bytes(data_frame=struct.pack("B", i))
            # transmitter.set_latest_bytes(struct.pack(""))
            sleep(0.1)
    sleep(10)
    transmitter.stop()


if __name__ == "__main__":
    main()

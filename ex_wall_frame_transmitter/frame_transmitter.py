import time

import numpy as np
from ex_wall_frame_transmitter.websocket_handler import WebsocketTransmitter
from ex_wall_frame_transmitter.frame_formatter import Frame


class FrameTransmitter:
    def __init__(self, destination_uri: str):
        self._destination_uri = destination_uri
        self._websocket_handler = WebsocketTransmitter(destination_uri=destination_uri)

    def start(self):
        self._websocket_handler.start()

    def stop(self):
        self._websocket_handler.stop()

    def send_numpy_frame(self, pid_gain: int, np_frame: np.array) -> None:
        frame = Frame(pid_gain=pid_gain, np_frame=np_frame)
        data_frame = frame.get_bytes()
        self._websocket_handler.set_latest_bytes(data_frame=data_frame)


def main():
    import logging
    logging.getLogger("main")
    logging.basicConfig(level="DEBUG")
    from ex_wall_frame_transmitter.constants import WIDTH, HEIGHT
    from decouple import config
    destination_uri = config("DESTINATION_URI")
    frame_transmitter = FrameTransmitter(destination_uri=destination_uri)
    frame_transmitter.start()
    fake_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=int)
    for h in range(HEIGHT):
        for w in range(WIDTH):
            fake_frame[h, w] = [255, 0, 0]
    frame_transmitter.send_numpy_frame(pid_gain=30, np_frame=fake_frame)
    time.sleep(1)
    frame_transmitter.stop()


if __name__ == "__main__":
    main()

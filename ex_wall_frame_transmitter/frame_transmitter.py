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

    def send_numpy_frame(self, np_frame: np.array) -> None:
        frame = Frame(np_frame=np_frame)
        data_frame = frame.get_bytes()
        self._websocket_handler.set_latest_bytes(data_frame=data_frame)

from ex_wall_frame_transmitter.constants import HEIGHT, WIDTH, MAPPING, NUM_PIXELS
import numpy as np
import struct


def _get_payload(color_list) -> bytes:
    string_format = "@" + "".join(["B" for _ in range((NUM_PIXELS * 3) + 1)])

    led_rgb_list = list()
    for r, g, b in color_list:
        led_rgb_list += [r, g, b]
    args = [30] + led_rgb_list
    payload = struct.pack(string_format, *args)
    return payload


class Frame:
    def __init__(self, np_frame: np.array):
        self.np_frame = np.clip(np_frame.astype(int), 0, 255)

    def get_bytes(self) -> bytes:
        pixels = [(0, 0, 0) for _ in range(NUM_PIXELS)]
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if MAPPING[y][x] is not None:
                    pixel = self.np_frame[y, x]
                    pixel_number = MAPPING[y][x]
                    pixels[pixel_number] = pixel[:3]
        frame_data = _get_payload(color_list=pixels)
        return frame_data

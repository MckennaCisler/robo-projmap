import project
import numpy as np
from time import time

class FPSRecorder:
    def __init__(self, print_frequency=1.0, averaging=0.9):
        self.last_time = time()
        self.last_print = 0
        self.frame_time = 1 / 60.0
        self.print_frequency = print_frequency
        self.averaging = averaging

    def record_frame(self):
        t = time()
        self.frame_time *= self.averaging
        self.frame_time += (1 - self.averaging) * (t - self.last_time)
        self.last_time = t

        if t - self.last_print > self.print_frequency:
            print('FPS: %0.0f' % (1 / self.frame_time, ))
            self.last_print = t

color = np.array([
    255, 255, 255,
    255, 255, 255,
    255, 255, 255, 
    255, 255, 255,
    255, 255, 255,
    255, 255, 255,
    255, 255, 255,
], dtype=np.int32)

xyd = np.array([
    -1., -1., 0.,
    1., -1., 0.,
    0.,  1., 0.,
    -3., -1., 0.,
    -2.,  1., 0.,
    3., -1., 0.,
    2.,  1., 0.,
], dtype=np.float32)

indices = np.array([
        3, 0, 4,
        0, 1, 2,
        1, 5, 6,
], dtype=np.int32)

project.start()
fps = FPSRecorder(averaging=0.0)
while True:
    if project.draw_frame(color, xyd, indices):
        project.stop()
        break
    else:
        fps.record_frame()

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

xyd = np.array([
    -1, -1, 0,  0, 0, 1,
    1, -1, 0,   0, 1, 0,
    0,  1, 0,   1, 0, 0,
    -3, -1, 0,  0, 1, 1,
    -2,  1, 0,  1, 1, 0,
    3, -1, 0,   1, 0, 1,
    2,  1, 0,   1, 1, 1
], dtype=np.float32)

mvp = np.array([
        1., -.2, 0., 0.,
        .2,  1., 0., 0.,
        0.,  0., 1., 0.,
        0.,  0., 0., 2.
], dtype=np.float32)

project.start(mvp, -1)
fps = FPSRecorder(averaging=0.0)
while True:
    if project.draw_frame(xyd):
        project.stop()
        break
    else:
        fps.record_frame()

import project
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

project.start()
fps = FPSRecorder(averaging=0.0)
while True:
    if project.draw_frame():
        project.stop()
        break
    else:
        fps.record_frame()

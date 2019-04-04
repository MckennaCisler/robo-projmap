import project
import numpy as np

class Projector():
    def __init__(self, calibration_matrix, *, y_res, x_res):
        self.calibration_matrix = calibration_matrix
        self.inds = np.indices([y_res, x_res], dtype=np.float32).transpose([1, 2, 0])
        #project.start()

    def draw_frame(self, rgb, depth):
        depth = np.expand_dims(depth, -1)
        coords = np.concatenate([
            self.inds * depth,
            depth,
            rgb
        ], -1)
        #project.draw_frame(coords)

    def __del__(self):
        #project.stop()
        pass


if __name__ == '__main__':
    p = Projector(np.zeros([4, 4]), y_res=1080, x_res=1920)
    rgb = np.zeros([1080, 1920, 3], dtype=np.uint8)
    depth = np.zeros([1080, 1920], dtype=np.float32)
    for i in range(100):
        p.draw_frame(rgb, depth)

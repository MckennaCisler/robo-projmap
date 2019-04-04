import project
import numpy as np

class Projector():
    def __init__(self, calibration_matrix, *, y_res, x_res):
        self.calibration_matrix = self.calibration_matrix
        self.inds = np.indices([y_res, x_res]).T
        project.start()

    def draw_frame(self, rgb, depth):
        depth = np.expand_dims(depth, -1)
        coords = np.concatenate([
            self.inds * depth,
            depth,
            rgb
        ], -1)
        project.draw_frame(coords)

    def __del__(self):
        project.stop()

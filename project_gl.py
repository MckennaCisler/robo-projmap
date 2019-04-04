import project
import numpy as np
import time
import cv2

class Projector():
    def __init__(self, calibration_matrix, *, x_res, y_res, proj_x_res=1366, proj_y_res=768):
        self.calibration_matrix = calibration_matrix.astype(np.float32)
        self.inds = np.indices([y_res, x_res], dtype=np.float32).transpose([1, 2, 0])
        project.start(self.calibration_matrix, x_res, y_res, proj_x_res, proj_y_res, -1)

    def draw_frame(self, rgb, depth):
        depth = np.expand_dims(depth, -1)
        coords = np.concatenate([
            self.inds * depth,
            depth,
            rgb/255.0
        ], -1)
        project.draw_frame(coords.astype(np.float32))

    def __del__(self):
        project.stop()
        pass


if __name__ == '__main__':
    fps = 60
    # width, height = 1000, 1000
    # width, height = 500, 250
    width, height = 768, 768
    
    mvp = np.array([
        0.,  -.1, 0., 0.,
        .1,  0., 0., 0.,
        0.,  0., 0., 120.,
        0.,  0., 0., .1
    ], dtype=np.float32)

    p = Projector(mvp, x_res=width, y_res=height,proj_x_res=1920, proj_y_res=1080)

    # rgb = 255*np.random.rand(height, width, 3)
    # rgb = 255*np.ones([height, width, 3], dtype=np.float32)
    # rgb[:,:,0] = 255 # r
    # rgb[:,:,1] = 0 # g
    # rgb[:,:,1] = 0 # b
    rgb = cv2.imread("testing_cat.jpg").astype(np.float32)
    # rgb = cv2.imread("testing.png").astype(np.float32)
    rgb = rgb[:height,:width,:]
    print(rgb)

    depth = np.ones([height, width], dtype=np.float32)

    for i in range(200):
        start = time.time()
        p.draw_frame(rgb, depth)
        time.sleep(max(0, 1. / fps - (time.time() - start)))

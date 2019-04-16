import project
import numpy as np
import time
import cv2
import matplotlib.pyplot as plt

class Projector():
    def __init__(self, calibration_matrix, *, x_res, y_res, proj_x_res=1366, proj_y_res=768, entire=False):
        A = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=np.float32)
        B = np.array([
            [1 / proj_x_res,    0,              0, 0],
            [0,                 1 / proj_y_res, 0, 0],
            [0,                 0,              1, 0],
            [0,                 0,              0, 0.5]
        ], dtype=np.float32)
        C = np.array([
            [1,  0,  0, -1],
            [0,  -1,  0,  1],
            [0,  0,  1,  0],
            [0,  0,  0,  1]
        ], dtype=np.float32)

        M = np.matmul(np.matmul(C, B), np.matmul(A, calibration_matrix))
        if entire:
            M = calibration_matrix

        M /= M[3, 3]
        print(M)
        self.calibration_matrix = np.ascontiguousarray(M.astype(np.float32))
        self.inds = np.indices([y_res, x_res], dtype=np.float32).transpose([1, 2, 0])[..., ::-1]
        project.start(self.calibration_matrix, x_res, y_res, proj_x_res, proj_y_res, -1)

    def draw_frame(self, rgb, depth):
        t1 = time.time()
        depth = np.expand_dims(depth, -1)
        coords = np.concatenate([
            self.inds * depth,
            depth,
            rgb / 255.0
        ], -1)

        t2 = time.time()

        df =  project.draw_frame(coords.astype(np.float32))
        t3 = time.time()

        print(t2 - t1, t3 - t2)
        return df


    def __del__(self):
        project.stop()
        pass


if __name__ == '__main__':
    fps = 60
    # width, height = 1000, 1000
    # width, height = 501, 500
    width, height = 1366, 768

    # mvp = np.array([
    #     0.,  -.1, 0., 0.,
    #     .1,  0., 0., 0.,
    #     0.,  0., 0., 40.,
    #     0.,  0., 0., .1
    # ], dtype=np.float32)
    mvp = np.array([
        [1/1366.,  0,    0,  -0.5],
        [0,  -1/768.,    0,  0.5],
        [0,  0,          0,  0],
        [0.0, 0.0,      0,  0.5]
    ], dtype=np.float32)
    # mvp = np.ascontiguousarray(mvp.T)

    p = Projector(mvp, x_res=width, y_res=height, proj_x_res=1366, proj_y_res=768, entire=True)

    # rgb = 255*np.random.rand(height, width, 3)
    # rgb = 255*np.ones([height, width, 3], dtype=np.float32)
    # rgb[:,:,0] = 255 # r
    # rgb[:,:,1] = 0 # g
    # rgb[:,:,1] = 0 # b
    rgb = cv2.imread("testing_cat.jpg").astype(np.float32)
    # rgb = cv2.imread("testing.png").astype(np.float32)
    rgb = rgb[:height,:width,:]

    depth = np.ones([height, width], dtype=np.float32)

    for i in range(500):
        start = time.time()
        if p.draw_frame(rgb, depth):
            break
        time.sleep(max(0, 1. / fps - (time.time() - start)))

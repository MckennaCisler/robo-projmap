import numpy as np
import time
import pickle

from project_gl import Projector

width, height = 1920, 1080

M = pickle.load(open('direct_model/correspondances/one_matrix.pickle', 'rb'))
M = np.concatenate([
    M,
    [[0, 0, 0, 0]]
], 0)

p = Projector(M, x_res=width, y_res=height, proj_x_res=1366, proj_y_res=768, monitor=1)

from kinect import Kinect
k = Kinect()
k.start()

# depth = 1000 * np.ones([height, width], dtype=np.float32)
while True:
    # rgb = 255*np.random.rand(height, width, 3)
    # rgb = np.random.randint(0, 255, size=[height, width, 3])
    rgb, depth = k.get_current_rgbd_frame()
    if p.draw_frame(255 - rgb[..., :3] , depth):
        p.stop()

k.stop()

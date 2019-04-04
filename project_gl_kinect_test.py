import numpy as np
import time
import pickle

from project_gl import Projector

# width, height = 1000, 1000
# width, height = 501, 500
width, height = 1920, 1080

mvp = np.array([
    1/1366.,  0,    0,  0,
    0,  -1/768.,    0,  0,
    0,  0,          0,  0,
    -0.5, 0.5,      0,  0.5
], dtype=np.float32)

M = pickle.load(open('correspondances/one_matrix.pickle', 'rb'))
M = np.concatenate([
    M,
    [[0, 0, 0, 1]]
], 0)

p = Projector(M, x_res=width, y_res=height, proj_x_res=1366, proj_y_res=768)


from kinect import Kinect
k = Kinect()
k.start()

depth = 1000*np.ones([height, width], dtype=np.float32)
for i in range(500):
    # rgb = 255*np.random.rand(height, width, 3)
    rgb = k.get_current_color_frame()
    # rgb, depth = k.get_current_rgbd_frame()
    p.draw_frame(rgb[..., :3], depth)

k.stop()
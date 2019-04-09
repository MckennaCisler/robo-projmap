import json
import numpy as np
from kinect import Kinect
from project import Fullscreen_Window
import pickle
from drawing_window import DrawingWindow
from time import sleep
import time
import cv2


M = pickle.load(open('direct_model/correspondances/one_matrix.pickle', 'rb'))
# M = np.array([
#     [1, 0, 0, 0],
#     [0, 1, 0, 0],
#     [0, 0, 1, 0],
# ])


k = Kinect()
k.start()

dr = DrawingWindow()
dr.update()

for i in range(100):
    print(i)
    rgb, _ = k.get_current_rgbd_frame(copy=True)
    dr.last_kinect_frame = rgb[..., :3]
    dr.update()

dr.close()

w = Fullscreen_Window()
w.clear()
w.update()


for i in range(500):
    rgb, d = k.get_current_rgbd_frame(copy=False)

    locs = np.array(dr.circles)
    print('circle shapes', locs.shape)
    rgb[..., 2] = np.logical_or(d > 5000, d < 150) * 255
    cv2.imshow('color', rgb)
    cv2.waitKey(1)

    x_coords, y_coords = locs[:, 0], locs[:, 1]
    d_coord = d[y_coords, x_coords].flatten()

    print(d_coord.shape, x_coords.shape, y_coords.shape)
    valid = np.logical_and(d_coord < 5000, d_coord > 150)
    d_coord_i = d_coord[valid]
    x_coords_i = x_coords[valid]
    y_coords_i = y_coords[valid]

    coords = np.stack([
        x_coords_i * d_coord_i,
        y_coords_i * d_coord_i,
        d_coord_i,
        np.ones(x_coords_i.shape)
    ], -1)

    proj_coords = np.matmul(M, coords.T).T
    proj_coords = proj_coords[..., :2] / proj_coords[..., 2:3]

    w.clear()
    w.draw_points(proj_coords[..., 0].flatten(), proj_coords[..., 1].flatten(), fill='white', s=12, outline='white')

    k.release_frames()
    time.sleep(0.05)

rgb  = k.get_current_color_frame()
cv2.imwrite('testing.png', rgb)

k.stop()

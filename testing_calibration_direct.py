import json
import numpy as np
from kinect import Kinect
from camera import Camera
from project_tk import Fullscreen_Window
import time
import cv2
import matplotlib.pyplot as plt
import pickle

GRID_VS_LINE = True

w = Fullscreen_Window()
w.clear()
w.update()

M = pickle.load(open('correspondances/one_matrix.pickle', 'rb'))
# M = np.array([
#     [1, 0, 0, 0],
#     [0, 1, 0, 0],
#     [0, 0, 1, 0],
# ])

if GRID_VS_LINE:
    gridshape = (30, 60)
    rows, cols = np.indices(gridshape)
    rows = (1080 * rows / gridshape[0]).astype(np.int32)
    cols = (1920 * cols / gridshape[1]).astype(np.int32)
    y_coords = rows.flatten()
    x_coords = cols.flatten()
else:
    y_coords = np.ones([1920]) * 1080 / 2
    x_coords = np.arange(1920)

k = Kinect()
k.start()

for i in range(500):
    start = time.time()
    rgb, d = k.get_current_rgbd_frame(copy=False)
    rgb[..., 2] = np.logical_or(d > 5000, d < 150) * 255
    print("kinect time: %f\t" % (time.time() - start), end="")
    cv2.imshow('color', rgb)
    cv2.waitKey(1)

    start = time.time()

    if GRID_VS_LINE:
        d_coord = d[rows, cols].flatten()
    else:
        d_coord = d[540, :]

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


    print("math time: %f\t" % (time.time() - start), end="")

    start = time.time()
    w.clear()
    w.draw_points(proj_coords[..., 0].flatten(), proj_coords[..., 1].flatten(), fill='white', s=5, outline='white')
    print("drawing time: %f" % (time.time() - start))

    k.release_frames()
    time.sleep(0.05)

rgb  = k.get_current_color_frame()
cv2.imwrite('testing.png', rgb)

k.stop()

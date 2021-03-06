import sys
sys.path.append("..")
import json
import numpy as np
from kinect import Kinect
from camera import Camera
from project_tk import Fullscreen_Window
import time
import cv2
import matplotlib.pyplot as plt

GRID_VS_LINE = True

w = Fullscreen_Window()
w.clear()
w.update()

camera = Camera.fromJson('kinect_calib.json', x_res=1920, y_res=1080)
p_intr, p_dist, c_extr, p_extr = [np.array(a) for a in json.load(open('camera_proj_calib.json' ,'r'))]
print( json.load(open('camera_proj_calib.json' ,'r'))[1])

camera = camera.getCameraWithExtr(c_extr[2])
projector = Camera(p_intr, p_dist, x_res=1366, y_res=768).getCameraWithExtr(p_extr[2])

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
    print("kinect time: %f\t" % (time.time() - start), end="")
    cv2.imshow('color', rgb)
    cv2.waitKey(1)

    start = time.time()

    if GRID_VS_LINE:
        d_coord = d[rows, cols].flatten()
    else:
        d_coord = d[540, :]

    world_space = camera.get_world_space(y=y_coords, x=x_coords, depth=d_coord / 30.0)
    projector_space = np.round(projector.get_camera_space(world_space)).astype(np.int32)

    projector_space_valid = np.logical_and(
        np.logical_and(projector_space[..., 0] >= 0, projector_space[..., 0] < 1368),
        np.logical_and(projector_space[..., 1] >= 0, projector_space[..., 1] < 768))

    projector_space = projector_space[projector_space_valid, :]

    print("math time: %f\t" % (time.time() - start), end="")

    start = time.time()
    w.clear()
    w.draw_points(projector_space[..., 0].flatten(), projector_space[..., 1].flatten(), fill='white', s=5, outline='white')
    print("drawing time: %f" % (time.time() - start))

    k.release_frames()
    time.sleep(0.05)

rgb  = k.get_current_color_frame()
cv2.imwrite('testing.png', rgb)

k.stop()

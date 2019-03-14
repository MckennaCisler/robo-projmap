import json
import numpy as np
from kinect import Kinect
from camera import Camera
from project import Fullscreen_Window
from time import sleep
import cv2
import matplotlib.pyplot as plt
from freenect2 import Device, FrameType
import gc

w = Fullscreen_Window()
w.clear()
w.update()

camera = Camera.fromJson('kinect_calib.json', x_res=1920, y_res=1080)
p_intr, p_dist, c_extr, p_extr = [np.array(a) for a in json.load(open('camera_proj_calib.json' ,'r'))]
camera = camera.getCameraWithExtr(c_extr[2])
projector = Camera(p_intr, p_dist, x_res=1366, y_res=768).getCameraWithExtr(p_extr[2])

y_coords = np.ones([1920]) * 1080 / 2
x_coords = np.arange(1920)

# k = Kinect()
# k.start()

device = Device()

j = 0
with device.running():
    for i in range(4):
        color = None
        for type_, frame1 in device:
                j += 1
                if j > 100:
                    break

                if type_ is FrameType.Color:
                    color = frame1
                elif type_ is FrameType.Depth and color is not None:
                    _, _, d = device.registration.apply(color, frame1, with_big_depth=True)
                    d = d.to_array()[1:-1,::-1]
                    # _, d = k.get_current_rgbd_frame() # (None, np.ones((1080, 1920)))

                    d_coord = d[540, :]

                    world_space = camera.get_world_space(y=y_coords, x=x_coords, depth=d_coord / 30.0)
                    projector_space = np.round(projector.get_camera_space(world_space)).astype(np.int32)

                    projector_space_valid = np.logical_and(
                        np.logical_and(projector_space[..., 0] >= 0, projector_space[..., 0] < 1368),
                        np.logical_and(projector_space[..., 1] >= 0, projector_space[..., 1] < 768))

                    projector_space = projector_space[projector_space_valid, :]

                    gc.collect()

                    # w.clear()
                    # w.draw_points(projector_space[..., 0].flatten(), projector_space[..., 1].flatten(), fill='white', s=5, outline='white')
                    # sleep(0.05)

# rgb,_  = k.get_current_rgbd_frame()
# cv2.imwrite('testing.png', rgb)

# k.stop()
print(projector_space)

import numpy as np
import matplotlib.pyplot as plt
from project import Fullscreen_Window
from kinect import *
from time import sleep
import cv2

def write_image(imname, im):
    im = np.copy(im)
    if im.shape[2] == 3:
        im = im[:, :, ::1]
    elif im.shape[2] == 4:
        im[:, :, :3] = im[:, :, 2::-1]
    cv2.imwrite(imname, im)

w = Fullscreen_Window()
w.clear()
w.update()
sleep(3)
k = Kinect()
k.start()
base_im = k.get_current_color_frame()

height, width = w.get_dims()
print('screen_dims:', width, height)

x_ims = []
for x in range(1, 16):
    w.clear()
    w.draw_line((width * x / 16, 0), (width * x / 16, height), fill='white', width=3)
    sleep(0.2)
    x_ims.append(k.get_current_color_frame())

y_ims = []
for y in range(1, 9):
    w.clear()
    w.draw_line((0, height * y / 9), (width, height * y / 9), fill='white', width=3)
    sleep(0.2)
    y_ims.append(k.get_current_color_frame())

k.stop()

print("writing images")
write_image('calibration_images/base.png', base_im)
for i, x_im in enumerate(x_ims):
    write_image('calibration_images/x_im%d.png' % (i,), x_im)
for i, y_im in enumerate(y_ims):
    write_image('calibration_images/y_im%d.png' % (i,), y_im)

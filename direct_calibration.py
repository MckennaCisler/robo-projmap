from project import Fullscreen_Window
from time import sleep
from kinect import Kinect
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import numpy as np

def get_me_some_correspondances(kinect, project):
    w.clear()
    sleep(0.25)
    base_im = kinect.get_current_color_frame()

    locs = [
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
    ]

    w.fill_circle(locs[0][0], locs[0][1], 20, 'red')
    w.fill_circle(locs[1][0], locs[1][1], 20, 'green')
    w.fill_circle(locs[2][0], locs[2][1], 20, 'blue')

    sleep(0.25)
    color_im = kinect.get_current_color_frame()

    imd = color_im / 255.0 - base_im / 255.0
    plt.imshow(imd + 0.5)
    imb = gaussian_filter(imd, [6, 6, 0])

    m = np.argmax(imb[..., 0] * 2 - imb[..., 1] - imb[..., 2])
    y, x = np.unravel_index(m, imb[..., 0].shape)
    l1 = (x, y)

    m = np.argmax(imb[..., 1] * 2 - imb[..., 0] - imb[..., 2])
    y, x = np.unravel_index(m, imb[..., 0].shape)
    l2 = (x, y)

    m = np.argmax(imb[..., 2] * 2 - imb[..., 1] - imb[..., 0])
    y, x = np.unravel_index(m, imb[..., 0].shape)
    l3 = (x, y)

    cam_locs = np.array([l1, l2, l3])
    proj_locs = np.array(locs)

    return cam_locs, proj_locs

w = Fullscreen_Window()
w.clear()
k = Kinect()
k.start()

cam_locs, proj_locs = get_me_some_correspondances(k, w)
plt.scatter(cam_locs[:, 0], cam_locs[:, 1])

k.stop()

plt.show()

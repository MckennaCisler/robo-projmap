import sys
sys.path.append("..")
from project_tk import Fullscreen_Window
from time import sleep
from kinect import Kinect
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import numpy as np
import pickle

def get_me_some_correspondances(kinect, project, x_res=1366, y_res=768, padding=20, gauss_filter_width=8.5):
    w.clear()
    sleep(0.25)
    base_im = kinect.get_current_color_frame()

    proj_locs = (np.random.rand(3, 2) * [[x_res - padding * 2, y_res - padding * 2]]) + padding
    diffs = np.expand_dims(proj_locs, 0) - np.expand_dims(proj_locs, 1)
    dd = np.sum(diffs**2, -1)

    while np.min(dd[dd != 0]) < 10000:
        proj_locs = (np.random.rand(3, 2) * [[x_res - padding * 2, y_res - padding * 2]]) + padding
        diffs = np.expand_dims(proj_locs, 0) - np.expand_dims(proj_locs, 1)
        dd = np.sum(diffs**2, -1)

    for proj_loc, color in zip(proj_locs, ['red', 'green', 'blue']):
        w.draw_point(proj_loc[0], proj_loc[1], s=20, c=color)

    sleep(0.25)
    color_im, depth = kinect.get_current_rgbd_frame()

    delta_image = color_im[..., :3] / 255.0 - base_im[..., :3] / 255.0
    delta_image_blur = gaussian_filter(delta_image, [gauss_filter_width, gauss_filter_width, 0])

    high_contrast_image = np.dot(delta_image_blur, np.eye(3) - 1)
    amaxs = np.argmax(np.reshape(high_contrast_image, [-1, 3]), 0)
    cam_locs = np.stack(np.unravel_index(amaxs, high_contrast_image.shape[:2]), -1)

    print(cam_locs)
    cam_locs = np.concatenate([
        cam_locs[..., ::-1],
        depth[
            cam_locs[:, 0],
            cam_locs[:, 1]].reshape(-1, 1)
        ], -1)

    valid = np.logical_and(cam_locs[:, -1] > 200, cam_locs[:, -1] < 4000)

    return delta_image, cam_locs[valid], proj_locs[valid]

w = Fullscreen_Window()
w.clear()
k = Kinect()
k.start()

a = 0

all_cam_locs, all_proj_locs = [], []
for i in range(20):
    im, cam_locs, proj_locs = get_me_some_correspondances(k, w)
    im += 0.5

    all_cam_locs.append(cam_locs)
    all_proj_locs.append(proj_locs)

    print(cam_locs)

    for cl in cam_locs:
        plt.imshow(im[int(cl[1])-20:int(cl[1])+20, int(cl[0])-20:int(cl[0])+20])
        plt.scatter(20, 20, c='white')
        plt.savefig('correspondances/corr%d.png' % (a, ))
        a += 1
        plt.clf()
        plt.close()

    if i % 5 == 4:
        w.clear()
        sleep(7)

k.stop()

print('ending')
print(all_cam_locs)

all_cam_locs = np.concatenate(all_cam_locs, 0)
all_proj_locs = np.concatenate(all_proj_locs, 0)

print('pickling')
pickle.dump({'cam locs': all_cam_locs, 'proj_locs':all_proj_locs},
            open('correspondances/data.pickle', 'wb'))

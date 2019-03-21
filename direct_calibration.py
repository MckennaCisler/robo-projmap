from project import Fullscreen_Window
from time import sleep
from kinect import Kinect
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import numpy as np
import pickle

def get_me_some_correspondances(kinect, project):
    w.clear()
    sleep(0.25)
    base_im = kinect.get_current_color_frame()

    locs = [
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
        (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
    ]

    l = np.array(locs)
    diffs = np.expand_dims(l, 0) - np.expand_dims(l, 1)
    dd = np.sum(diffs**2, -1)

    while np.min(dd[dd != 0]) < 10000:
        locs = [
            (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
            (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
            (np.random.rand() * 1326 + 20, np.random.rand() * 728 + 20),
        ]

        l = np.array(locs)
        diffs = np.expand_dims(l, 0) - np.expand_dims(l, 1)
        dd = np.sum(diffs**2, -1)

    w.draw_point(locs[0][0], locs[0][1], s=20, c='red')
    w.draw_point(locs[1][0], locs[1][1], s=20, c='green')
    w.draw_point(locs[2][0], locs[2][1], s=20, c='blue')

    sleep(0.25)
    color_im, depth = kinect.get_current_rgbd_frame()

    imd = color_im / 255.0 - base_im / 255.0
    imd = imd[..., :3]
    imb = gaussian_filter(imd, [8.5, 8.5, 0])

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

    depths = [depth[cloc[1], cloc[0]] for cloc in cam_locs]
    cam_locs = np.concatenate(
        [cam_locs, np.array(depths).reshape(-1, 1)], -1
    )
    print(cam_locs)

    valid = np.logical_and(
        cam_locs[:, -1] > 200,
        cam_locs[:, -1] < 3000)

    return imd, cam_locs[valid], proj_locs[valid]

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
        #plt.savefig('correspondances/corr%d.png' % (a, ))
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

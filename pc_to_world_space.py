import cv2
import argparse
from os.path import join
import numpy as np
np.set_printoptions(suppress=True, precision=4)
import itertools
import matplotlib.pyplot as plt
import sys

def read_projector_calibration_images(directory):
    base_im = cv2.imread(join(directory, 'base.png'), cv2.IMREAD_GRAYSCALE)
    x_ims = [cv2.imread(join(directory, 'x_im%d.png' % (i, )), cv2.IMREAD_GRAYSCALE) for i in range(15)]
    y_ims = [cv2.imread(join(directory, 'y_im%d.png' % (i, )), cv2.IMREAD_GRAYSCALE) for i in range(8)]

    return base_im, x_ims, y_ims

def find_line(base_im, im, threshhold=0.1, dist=12):
    base_im = base_im.copy().astype(np.float32)
    im = im.copy().astype(np.float32)

    base_im /= np.mean(base_im)
    im /= np.mean(im)

    r, t = find_line_binary_image(im - base_im > threshhold)
    wt = np.maximum(im - base_im, 0)
    
    rs = np.sum(np.indices(wt.shape) * np.array([[[np.sin(t)]], [[np.cos(t)]]]), 0)
    wt[np.abs(rs - r) > dist] = 0
    wt -= 0.05
    wt[wt < 0] = 0

    inds = np.stack(np.where(wt), -1).astype(np.float32)
    wts = np.expand_dims(wt[wt>0], 1)

    mean = np.sum(wts * inds, 0) / np.sum(wts)
    inds -= mean

    vals, vec = (np.linalg.eig(np.matmul((wts*inds).T, (wts*inds))))
    big = np.argmax(np.abs(vals))
    small = np.argmin(np.abs(vals))

    rho = np.abs(np.dot(mean, vec[:, small]))
    theta = np.arctan2(vec[0, small], vec[1, small])

    if theta > t + np.pi / 2:
        theta -= np.pi
    if theta < t - np.pi / 2:
        theta += np.pi


    return rho, theta

    


def find_line_binary_image(im):
    rho, theta = cv2.HoughLines(im.astype(np.uint8), 1, np.pi / 180, 100, lines=1)[0, 0]
    return rho, theta

def find_line_intersection(line1_rt, line2_rt):
    r1, t1 = line1_rt
    r2, t2 = line2_rt

    arr = np.array([
        [np.cos(t1), np.sin(t1)],
        [np.cos(t2), np.sin(t2)]])
    arr_inv = np.linalg.inv(arr)
    return np.matmul(arr_inv, np.array([r1, r2]))


parser = argparse.ArgumentParser(description='convert the line crossings in projector space to points in world space on the image plane.')
parser.add_argument('--cam-cal', dest='camera_calibration_file', type=str)
parser.add_argument('--proj-cal-dir', dest='proj_im_dir', type=str, required=True)
args = parser.parse_args()


proj_im_dir = args.proj_im_dir
camera_calibration_file = args.camera_calibration_file

camera_calibration = None # TODO read calibration data from file

base_im, x_ims, y_ims = read_projector_calibration_images(proj_im_dir)

x_lines = [find_line(base_im, im) for im in x_ims]
y_lines = [find_line(base_im, im) for im in y_ims]


points = np.zeros([15, 8, 2])
for x in range(15):
    for y in range(8):
        points[x, y] = find_line_intersection(x_lines[x], y_lines[y])

plt.figure(figsize=[12, 8])
plt.imshow(x_ims[7])
plt.scatter(points[:, :, 0], points[:, :, 1], s=1)
plt.show()

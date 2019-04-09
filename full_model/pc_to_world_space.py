import cv2
import argparse
from os.path import join
import numpy as np
np.set_printoptions(suppress=True, precision=4)
import itertools
import matplotlib.pyplot as plt
import sys
import json

def read_projector_calibration_images(directory, camera):
    base_im = camera.load_image_grayscale(join(directory, 'base.png'))
    x_ims = [camera.load_image_grayscale(join(directory, 'x_im%d.png' % (i, ))) for i in range(15)]
    y_ims = [camera.load_image_grayscale(join(directory, 'y_im%d.png' % (i, ))) for i in range(8)]

    return base_im, x_ims, y_ims

def find_line(base_im, im, threshhold=0.1, dist=12):
    base_im = base_im.copy().astype(np.float32)
    im = im.copy().astype(np.float32)

    base_im /= np.mean(base_im)
    im /= np.mean(im)

    r, t = find_line_binary_image(im - base_im > threshhold)

    if r < 0:
        r *= -1
        t += np.pi
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

    while theta > t + np.pi / 2:
        theta -= np.pi
        rho *= -1
    while theta < t - np.pi / 2:
        theta += np.pi
        rho *= -1
    if np.sign(rho) != np.sign(r):
        rho *= -1

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

def get_intersection_points(proj_im_dir, camera, shape=(15, 8)):
    base_im, x_ims, y_ims = read_projector_calibration_images(proj_im_dir, camera)

    x_lines = [find_line(base_im, im) for im in x_ims]
    y_lines = [find_line(base_im, im) for im in y_ims]

    cam_points = np.zeros([shape[0], shape[1], 2])
    proj_points = np.zeros([shape[0], shape[1], 2])

    for x in range(shape[0]):
        for y in range(shape[1]):
            proj_points[x, y] = [1366 * (x+1) / 16.0, 768 * (y+1) / 9.0]
            cam_points[x, y] = find_line_intersection(x_lines[x], y_lines[y])

    return proj_points, cam_points

if __name__ == '__main__':
    points = get_intersection_points('calibration_images/proj_calib_2', 'kinect_calib.json')
    plt.scatter(points[..., 0], points[..., 1])
    plt.show()

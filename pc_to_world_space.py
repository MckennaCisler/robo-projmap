import cv2
import argparse
from os.path import join
import numpy as np
np.set_printoptions(suppress=True, precision=4)
import itertools

def read_projector_calibration_images(directory):
    base_im = cv2.imread(join(directory, 'base.png'), cv2.IMREAD_GRAYSCALE)
    x_ims = [cv2.imread(join(directory, 'x_im%d.png' % (i, )), cv2.IMREAD_GRAYSCALE) for i in range(15)]
    y_ims = [cv2.imread(join(directory, 'y_im%d.png' % (i, )), cv2.IMREAD_GRAYSCALE) for i in range(8)]

    return base_im, x_ims, y_ims

def find_line(base_im, im, threshhold=0.1):
    base_im = base_im.copy().astype(np.float32)
    im = im.copy().astype(np.float32)

    base_im /= np.mean(base_im)
    im /= np.mean(im)

    return find_line_binary_image(im - base_im > threshhold)

def find_line_binary_image(im):
    rho, theta = cv2.HoughLines(im.astype(np.uint8), 1, np.pi / 180, 100, lines=1)[0, 0]
    return rho, theta

def find_line_intersection(line1_rt, line2_rt):
    print(line1_rt, line2_rt)
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

print(points)

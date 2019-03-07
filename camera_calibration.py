#!/usr/bin/env python3
import numpy as np
import cv2
import kinect
import sys
from os.path import join
import matplotlib.pyplot as plt
import calibration

NUM_IMAGES = 20
IMAGE_DIR = "calibration_images/"
GRID_X_NUM = 7
GRID_Y_NUM = 5

def collect_calib_data(images):
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((GRID_Y_NUM*GRID_X_NUM,3), np.float32)
    objp[:,:2] = np.mgrid[0:GRID_X_NUM,0:GRID_Y_NUM].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    for i in range(len(images)):
        img = images[i]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, (GRID_X_NUM, GRID_Y_NUM), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
        else:
            print("WARNING: image %d: no corners found!" % i)

    print("found grid in %d/%d images" % (len(objpoints), len(images)))
    return objpoints, imgpoints

def capture_images(direc):
    print("writing %d frames to %s" % (NUM_IMAGES, direc))
    images = []
    for i in range(NUM_IMAGES):
        print("capturing")
        img = kinect.get_color_frame()
        print("done; hit enter to capture next")
        cv2.imshow('img', img)
        cv2.waitKey()

        fname = join(direc, "grid_calib_%d.png" % i)
        cv2.imwrite(fname, img)
        print("saved frame to %s" % fname)
        images.append(img)
    return images

def read_images(direc):
    print("reading %d frames from %s" % (NUM_IMAGES, direc))
    images = []
    for i in range(NUM_IMAGES):
        fname = join(direc, "grid_calib_%d.png" % i)
        images.append(cv2.imread(fname))
    return images

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print("usage: %s capture|calib [<image directory>] [<calibration filename>]" % sys.argv[0])
        exit(1)

    func = sys.argv[1].lower()
    if func == "capture":
        direc = sys.argv[2] if len(sys.argv) > 2 else IMAGE_DIR
        images = capture_images(direc)
    elif func == "calib":
        direc = sys.argv[2] if len(sys.argv) > 2 else IMAGE_DIR
        images = read_images(direc)
    else: 
        print("invalid function")
        exit(1)

    if len(images) == 0:
        print("no images captured or read")
        exit(1)

    # get grid data
    objpoints, imgpoints = collect_calib_data(images)

    if len(objpoints) == 0:
        print("No grids found in images")
        exit(1)

    # calibrate
    mtx, dist, rvecs, tvecs = calibration.calibrate_camera(objpoints, imgpoints, (images[0].shape[1::-1]))

    calibf = sys.argv[3] if len(sys.argv) > 3 else "camera_calib.json"
    print("saving calibration data to %s" % calibf)
    calibration.dump_calibration(calibf, mtx, dist, rvecs, tvecs)
    
    
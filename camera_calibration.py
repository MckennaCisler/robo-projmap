#!/usr/bin/env python
import numpy as np
import cv2 as cv
import kinect
import sys
from os.path import join
import matplotlib.pyplot as plt

NUM_IMAGES = 20
IMAGE_DIR = "calibration_images/"

def collect_calib_data(images):
    # termination criteria
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((5*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:5].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    for i in range(len(images)):
        img = images[i]
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (7,5), None)

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            # cv.drawChessboardCorners(img, (7,5), corners2, ret)
            # cv.imshow('img', img)
            # cv.waitKey()
        else:
            print("WARNING: no corners found!")


    cv.destroyAllWindows()

    print("found %d good images" % len(objpoints))
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    print("\nmatrix: \n%s\n" % mtx)
    print("\nrvecs: \n%s\n" % rvecs)
    print("\ntvecs: \n%s\n" % tvecs)

    mean_err, all_errors = calculate_reproj_error(objpoints, imgpoints, mtx, dist, rvecs, tvecs)
    print( "error: %f" % mean_err)
    # plt.hist(all_errors)
    plt.hist(np.sqrt(all_errors))
    plt.show()

    return objpoints, imgpoints

def calculate_reproj_error(objpoints, imgpoints, mtx, dist, rvecs, tvecs):
    mean_error = 0
    all_errors = []
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        all_errors.append(np.sum((imgpoints[i] - imgpoints2)**2, (1,2)))

        pnt_errors = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)
        error = pnt_errors/len(imgpoints2)
        mean_error += error
    all_errors = np.concatenate(all_errors, 0)
    return mean_error/len(objpoints), all_errors

def calibrate_camera(objpoints, imgpoints, imgshape):
    return cv.calibrateCamera(objpoints, imgpoints, imgshape, None, None)

def capture_images():
    images = []
    for i in range(NUM_IMAGES):
        print("capturing")
        img = kinect.get_color_frame()
        print("done")
        cv.imshow('img', img)
        cv.waitKey()

        fname = IMAGE_DIR + "grid_calib_%d.png" % i
        cv.imwrite(fname, img)
        print("saved frame to %s" % fname)
        images.append(img)
    return images

if __name__ == "__main__": 
    if len(sys.argv) != 2:
        print("usage: %s capture|calib" % sys.argv[0])
    
    if sys.argv[1].lower() == "capture":
        images = capture_images()
    else:
        images = []
        for i in range(20):
            fname = join(IMAGE_DIR, "grid_calib_pass_1", "grid_calib_%d.png" % i)
            images.append(cv.imread(fname))
    objpoints, imgpoints = collect_calib_data(images)

    # print(calibrate_camera(objpoints, imgpoints, images[0].shape[::-1]))
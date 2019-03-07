#!/usr/bin/python3
import numpy as np
import cv2
import json

def calibrate_camera(objpoints, imgpoints, imgshape):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (imgshape), None, None)
    return mtx, dist, rvecs, tvecs

def dump_calibration(fname, mtx, dist, rvecs, tvecs):
    with open(fname, "w") as f:
        json.dump((
            mtx.tolist(),
            dist.tolist(), 
            [r.tolist() for r in rvecs], 
            [t.tolist() for t in tvecs]),
        f, indent=4)

def load_calibration(fname):
    with open(fname, "r") as f:
        mtx, dist, rvecs, tvecs = json.load(f)
    rvecs = [np.array(r) for r in rvecs]
    tvecs = [np.array(t) for t in tvecs]
    return np.array(mtx), np.array(dist), rvecs, tvecs

def calculate_reproj_error(objpoints, imgpoints, mtx, dist, rvecs, tvecs):
    mean_error = 0
    square_errs = []
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        square_errs.append(np.sum((imgpoints[i] - imgpoints2)**2, (1,2)))

        pnt_errors = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)
        error = pnt_errors/len(imgpoints2)
        mean_error += error

    square_errs = np.concatenate(square_errs, 0)
    return mean_error/len(objpoints), square_errs
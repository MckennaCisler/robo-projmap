import numpy as np
import json
import cv2
np.set_printoptions(suppress=True, precision=4)
import matplotlib.pyplot as plt
from os.path import join
from pc_to_world_space import get_intersection_points
from camera import Camera, make_extrinsic
from calibration import calibrate_camera
import json

camera = Camera.fromJson('kinect_calib.json', x_res=1920, y_res=1080)

# print(locs)
# sys.exit(1)

wlocs = []
plocs = []
camera_extrs = []
for i, projector_dir in enumerate([
    'calibration_images/proj_calib_1',
    'calibration_images/proj_calib_2',
    'calibration_images/proj_calib_3']):

    GRID_X_NUM = 7
    GRID_Y_NUM = 5

    objp = np.zeros((GRID_Y_NUM*GRID_X_NUM,3), np.float32)
    objp[:,:2] = np.mgrid[0:GRID_X_NUM,0:GRID_Y_NUM].T.reshape(-1,2)

    base_im = camera.load_image_grayscale(join(projector_dir, 'base.png'))
    ret, corners = cv2.findChessboardCorners(base_im, (GRID_X_NUM, GRID_Y_NUM), None)

    # img = np.stack([base_im, base_im, base_im], -1)
    # cv2.drawChessboardCorners(img, (GRID_X_NUM, GRID_Y_NUM), corners, ret)
    # cv2.imshow('img', img)
    # cv2.waitKey(1000)

    worked, rvec, tvec = camera.solvePnP(objp, corners)
    camera_extrs.append(make_extrinsic(rvec, tvec))

    positioned_cam = camera.getCameraAtLoc(rvec, tvec)
    proj_points, cam_points = get_intersection_points(projector_dir, camera)

    world_space = positioned_cam.get_world_space(
                x=cam_points[...,0],
                y=cam_points[...,1],
                depth=np.ones(cam_points.shape[:-1]))
    dirs = world_space - positioned_cam.get_center()
    intersec_locations = world_space - dirs * (world_space[...,2:3] / dirs[...,2:3])
    intersec_locations = intersec_locations.reshape([-1, 3])

    wlocs.append(intersec_locations)
    plocs.append(proj_points.reshape([-1, 2]))

print(len(wlocs), wlocs[0].dtype, wlocs[0].shape)
print(len(plocs), plocs[0].dtype, plocs[0].shape)

intr, dist, rvecs, tvecs = calibrate_camera(wlocs, plocs, (1366, 768))

projector = Camera(intr, dist, x_res=1366, y_res=768)
projector_extrs = [make_extrinsic(rvec, tvec)
            for rvec, tvec in zip(rvecs, tvecs)]


json.dump((intr.tolist(), dist.tolist(), [a.tolist() for a in camera_extrs], [a.tolist() for a in projector_extrs]), open('camera_proj_calib.json', 'w'), indent=4)
for pextr, cextr in zip(projector_extrs, camera_extrs):
    print(np.matmul(pextr, np.linalg.inv(cextr)))

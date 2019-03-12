import numpy as np
import json
import cv2
np.set_printoptions(suppress=True, precision=4)
import matplotlib.pyplot as plt
from os.path import join
from pc_to_world_space import get_intersection_points
from camera import Camera
from calibration import calibrate_camera

camera = Camera.fromJson('kinect_calib.json', x_res=1920, y_res=1080)

# print(locs)
# sys.exit(1)

wlocs = []
plocs = []
for projector_dir in [
    'calibration_images/proj_calib_1',
    'calibration_images/proj_calib_3']:

    GRID_X_NUM = 7
    GRID_Y_NUM = 5

    objp = np.zeros((GRID_Y_NUM*GRID_X_NUM,3), np.float32)
    objp[:,:2] = np.mgrid[0:GRID_X_NUM,0:GRID_Y_NUM].T.reshape(-1,2)

    base_im = camera.load_image_grayscale(join(projector_dir, 'base.png'))
    ret, corners = cv2.findChessboardCorners(base_im, (GRID_X_NUM, GRID_Y_NUM), None)
    worked, rvec, tvec = camera.solvePnP(objp, corners)

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
a, _ = cv2.projectPoints(wlocs[0], rvecs[0], tvecs[0], intr, dist)
b, _ = cv2.projectPoints(wlocs[0] * 1.1, rvecs[0], tvecs[0], intr, dist)
# projector = Camera(intr, np.array([0.0, 0, 0, 0, 0]), x_res=1366, y_res=768).getCameraAtLoc(rvecs[1], tvecs[1])
# a = projector.get_camera_space(wlocs[1])
plt.scatter(a[...,0], a[...,1])
plt.scatter(b[...,0], b[...,1])
plt.xlim([0, 1366])
plt.ylim([0, 768])
plt.show()

newcameramtx, roi = cv2.getOptimalNewCameraMatrix(intr,dist,(1366,768),1,(1366,768))
print(newcameramtx)
print(roi)
dst = cv2.undistort(cv2.imread('testing_cat.jpg')[...,::-1], intr, dist, None, newcameramtx)
plt.imshow(dst)
plt.show()

projector = Camera(intr, dist, x_res=1366, y_res=768)
proj = projector.getCameraAtLoc(rvecs[0], tvecs[0])

c = proj.get_camera_space(wlocs[0])
plt.scatter(c[...,0], c[...,1])
plt.xlim([0, 1366])
plt.ylim([0, 768])
plt.show()

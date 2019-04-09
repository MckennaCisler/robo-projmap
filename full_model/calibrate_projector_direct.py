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

def fit_homog_matrix(coord1s, coord2s):
    assert coord1s.shape[0] == coord2s.shape[0]
    points = coord1s.shape[0]

    outs = coord1s.shape[1]
    ins = coord2s.shape[1]
    M = np.zeros([outs + 1, ins + 1])
    A = np.zeros([points * outs, (outs + 1) * (ins + 1)])

    for i in range(outs):
        A[i::outs, (ins+1)*i:(ins+1)*i+ins] = coord2s
        A[i::outs, (ins+1)*(i)+ins] = 1

    for i in range(outs):
        ii = (ins + 1) * (outs)
        A[i::outs, ii:ii+ins] = -coord2s * coord1s[:, i:i+1]
        A[i::outs, ii+ins] = -coord1s[:, i]

    AtA = np.matmul(A.T, A)
    vals, vecs = np.linalg.eig(AtA)

    vec = vecs[:, np.argmin(np.abs(vals))]

    return np.reshape(vec, M.shape)

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
    cextr = make_extrinsic(rvec, tvec)

    forward_vector = np.matmul(np.linalg.inv(cextr), np.array([[0], [0], [1], [0]]))
    forward_vector /= np.linalg.norm(forward_vector)

    positioned_cam = camera.getCameraAtLoc(rvec, tvec)
    proj_points, cam_points = get_intersection_points(projector_dir, camera)

    world_space = positioned_cam.get_world_space(
                x=cam_points[...,0],
                y=cam_points[...,1],
                depth=np.ones(cam_points.shape[:-1]))
    dirs = world_space - positioned_cam.get_center()
    intersec_locations = world_space - dirs * (world_space[...,2:3] / dirs[...,2:3])
    intersec_locations = intersec_locations.reshape([-1, 3])

    deltas = intersec_locations -  positioned_cam.get_center()
    depth = np.dot(deltas, forward_vector[:3, 0])

    wloc = np.concatenate([
        cam_points.reshape([-1, 2]),
        np.expand_dims(depth, -1)
    ], -1)

    wlocs.append(wloc)
    plocs.append(proj_points.reshape([-1, 2]))


wlocs = np.concatenate(wlocs, 0)
plocs = np.concatenate(plocs, 0)

M = fit_homog_matrix(plocs, wlocs)
wlocs = np.concatenate([
    wlocs,
    np.ones(list(wlocs.shape)[:-1] + [1])
], -1)

hlocs = np.matmul(M, wlocs.T).T
locs = hlocs[:, :2] / hlocs[:, 2:3]
print(np.mean((plocs - locs)**2))

plt.scatter(locs[:, 0], locs[:, 1], c='blue')

wlocs[:, 2] += 1
hlocs = np.matmul(M, wlocs.T).T
locs = hlocs[:, :2] / hlocs[:, 2:3]
plt.scatter(locs[:, 0], locs[:, 1], c='green')
plt.scatter(plocs[:, 0], plocs[:, 1], c='red')



plt.show()

import json
import numpy as np
import cv2

def make_extrinsic(rvec, tvec):
    rotation_matrix = eulerAnglesToRotationMatrix(rvec.flatten())
    extrinsic = np.concatenate([rotation_matrix, tvec], 1)
    return np.concatenate([extrinsic, np.array([[0, 0, 0, 1]])], 0)



def eulerAnglesToRotationMatrix(theta):
    R_x = np.array([[1,         0,                  0                   ],
                    [0,         np.cos(theta[0]), -np.sin(theta[0]) ],
                    [0,         np.sin(theta[0]), np.cos(theta[0])  ]
                    ])
    R_y = np.array([[np.cos(theta[1]),    0,      np.sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-np.sin(theta[1]),   0,      np.cos(theta[1])  ]
                    ])
    R_z = np.array([[np.cos(theta[2]),    -np.sin(theta[2]),    0],
                    [np.sin(theta[2]),    np.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])
    return np.dot(R_z, np.dot( R_y, R_x ))



class PositionalCamera:
    def __init__(self, camera_mat, resolution):
        self.camera_mat = camera_mat
        self.resolution = np.array(resolution)

        self.camera_mat_extended = np.concatenate([self.camera_mat, np.array([[0, 0, 0, 1]])], 0)
        self.camera_mat_inv = np.linalg.inv(self.camera_mat_extended)[:-1]

    def get_center(self):
        return np.copy(self.camera_mat_inv[:3, 3])

    def get_camera_space(self, coords):
        if coords.shape[-1] == 3:
            homo_coords = np.concatenate([
                coords,
                np.ones(list(coords.shape[:-1]) + [1], dtype=coords.dtype)], -1)
        elif coords.shape[-1] == 4:
            homo_coords = coords
        else:
            return None

        homo_camera = np.dot(homo_coords, self.camera_mat.T)
        return homo_camera[..., :2] / homo_camera[..., 2:3]

    def get_world_space(self, *, y, x, depth):
        y, x, depth = np.array(y), np.array(x), np.array(depth)

        homogeneous_camera_coords = \
            np.stack([
                x * depth,
                y * depth,
                depth,
                np.ones(x.shape)
            ], -1)

        return np.dot(homogeneous_camera_coords, self.camera_mat_inv.T)

    def resize(self, new_resolution):
        new_resolution = np.array(new_resolution)
        res_change = new_resolution / self.resolution

        new_camera_mat = np.matmul(
            [
                [res_change[0], 0, 0],
                [0, res_change[1], 0],
                [0, 0,             1]
            ],
            self.camera_mat)

        return PositionalCamera(new_camera_mat, new_resolution)

class Camera:
    @staticmethod
    def fromJson(calibration_file, *, x_res, y_res):
        loads = json.load(open(calibration_file, 'r'))
        intr, dist, _, _ = [np.array(load) for load in loads]
        return Camera(intr, dist, x_res=x_res, y_res=y_res)

    def __init__(self, intr, dist, *, x_res, y_res):
        self.intr, self.dist = intr, dist

        self.w = x_res
        self.h = y_res

        self.nintr, self.roi = cv2.getOptimalNewCameraMatrix(
                                        self.intr,
                                        self.dist,
                                        (self.w, self.h),
                                        1,
                                        (self.w, self.h))

    def load_image(self, filename):
        im = cv2.imread(filename)[...,::-1]
        return cv2.undistort(im, self.intr, self.dist, None, self.nintr)

    def load_image_grayscale(self, filename):
        im = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

        if im is None:
            print(filename, 'does not exist')

        im2 = cv2.undistort(im, self.intr, self.dist, None, self.nintr)
        return im2

    def solvePnP(self, world_points, image_points):
        return cv2.solvePnP(world_points, image_points, self.nintr, None)

    def getCameraAtLoc(self, rvec, tvec):
        rotation_matrix = eulerAnglesToRotationMatrix(rvec.flatten())
        extrinsic = np.concatenate([rotation_matrix, tvec], 1)
        camera_matrix = np.matmul(self.nintr, extrinsic)
        return PositionalCamera(camera_matrix, [self.w, self.h])

    def getCameraWithExtr(self, extrinsic):
        rotation_matrix = eulerAnglesToRotationMatrix(rvec.flatten())
        extrinsic = extrinsic[:3, :4]
        camera_matrix = np.matmul(self.nintr, extrinsic)
        return PositionalCamera(camera_matrix, [self.w, self.h])

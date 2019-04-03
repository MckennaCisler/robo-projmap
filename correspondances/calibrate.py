import numpy as np
import pickle
import matplotlib.pyplot as plt

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

def homogenize(coords):
    ones_shape = list(coords.shape[:-1]) + [1]
    return np.concatenate([coords, np.ones(ones_shape)], -1)

def dehomogenize(coords):
    return coords[..., :-1] / coords[..., -1:]


######################### LOAD GOOD CORRESPONDANCES #####################
bad_inds = [3, 5, 7, 9, 18, 20, 22, 25, 27, 33, 41, 45]
corres = pickle.load(open('data.pickle', 'rb'))
cam_locs, proj_locs = corres['cam locs'], corres['proj_locs']
want = np.ones((cam_locs.shape[0]), dtype=bool)
want[bad_inds] = False
cam_locs, proj_locs = cam_locs[want], proj_locs[want]


###################### SOLVE AFFINE TRANSFORMATION MATRIX ###############
cam_locs_2d = np.copy(cam_locs[..., :2])
M_affine = fit_homog_matrix(proj_locs, cam_locs_2d)
affine_preditions = dehomogenize(np.matmul(homogenize(cam_locs_2d), M_affine.T))

###################### SOLVE CAMERA MATRIX ##############################
cam_locs_3d = np.copy(cam_locs)
cam_locs_3d[..., :2] *= cam_locs_3d[..., 2:3]

M_full = fit_homog_matrix(proj_locs, cam_locs_3d)
full_preditions = dehomogenize(np.matmul(homogenize(cam_locs_3d), M_full.T))


###################### PLOT ERROR AS IMAGE ##########################
plt.scatter(proj_locs[:, 0], proj_locs[:, 1], c='black')
plt.scatter(affine_preditions[:, 0], affine_preditions[:, 1], c='red', alpha=0.6)
plt.scatter(full_preditions[:, 0], full_preditions[:, 1], c='blue', alpha=0.6)
plt.show()


##################### PLOT ERROR TOTAL ##############################

plt.figure(figsize=[8, 8])
affine_errors = affine_preditions - proj_locs
full_errors = full_preditions - proj_locs
plt.scatter(affine_errors[:, 0], affine_errors[:, 1], s=70, alpha=0.5, c='red', label='Affine Reprojection')
plt.scatter(full_errors[:, 0], full_errors[:, 1], s=70, alpha=0.5, c='blue', label='Camera Matrix Robrojection')
plt.xlim([-60, 60])
plt.ylim([-60, 60])
plt.legend(loc='upper right')
plt.title('Reprojection Error: Affine Transformation vs Full Camera Matrix')
plt.show()


####################### SAVE FULL MATRIX ###########################
pickle.dump(M_full, open('one_matrix.pickle', 'wb'))

print(np.concatenate([proj_locs, full_preditions], 1))

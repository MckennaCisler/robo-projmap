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

bad_inds = [8, 16, 17, 20, 32, 34, 37, 45]
np.ones((2, 2), dtype=bool)
corres = pickle.load(open('data.pickle', 'rb'))
cam_locs = corres['cam locs']
proj_locs = corres['proj_locs']
want = np.ones((cam_locs.shape[0]), dtype=bool)
for bad in bad_inds:
    want[bad] = False

proj_locs = proj_locs[want]
cam_locs = cam_locs[want]
cam_locs[:, :2] = cam_locs[:, :2] * cam_locs[:, 2:3]

M = fit_homog_matrix(proj_locs, cam_locs)
pickle.dump(M, open('one_matrix.pickle', 'wb'))
ones_shape = list(cam_locs.shape[:-1]) + [1]
homog = np.concatenate([cam_locs, np.ones(ones_shape)], -1)
pred = np.matmul(M, homog.T).T
pred = pred[:, :2] / pred[:, 2:3]

plt.scatter(proj_locs[:, 0], proj_locs[:, 1], c='red')
plt.scatter(pred[:, 0], pred[:, 1], c='blue')
plt.show()

print(np.concatenate([proj_locs, pred], 1))

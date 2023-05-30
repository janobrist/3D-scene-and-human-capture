import sys
import os
import json
import numpy as np
import open3d as o3d
import colorsys

def read_json_as_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

if __name__ == '__main__':
    ns_transform_path = 'outputs/unnamed/nerfacto/2023-05-26_082508/dataparser_transforms.json'
    mocap_kpts_dir = 'data/final/mocap/output/keypoints3d/'

    output_dir = 'data/final/mocap/output/'

    ns_trans_params = read_json_as_dict(ns_transform_path)
    R_ns = np.vstack(
        (ns_trans_params['transform'][0][:3], ns_trans_params['transform'][1][:3], ns_trans_params['transform'][2][:3]))
    t_ns = np.hstack(
        (ns_trans_params['transform'][0][3], ns_trans_params['transform'][1][3], ns_trans_params['transform'][2][3]))
    scale_ns = ns_trans_params['scale']

    mocap_kpts_names = os.listdir(mocap_kpts_dir)
    mocap_kpts_names.sort()

    mocap_kpts = []
    mocap_kpt_ids = []

    for name in mocap_kpts_names:
        temp = read_json_as_dict(mocap_kpts_dir + name)
        mocap_kpts.append(np.array(temp[0]['keypoints3d']))
        mocap_kpt_ids.append(temp[0]['id'])

    mocap_kpts = np.array(mocap_kpts)

    # transform keypoints
    ns_kpts = np.zeros_like(mocap_kpts)

    for frame in range(mocap_kpts.shape[0]):
        xyz = mocap_kpts[frame, :, :3]
        # transform mocap points to ns points
        xyz_trans = np.zeros_like(xyz)
        for i in range(xyz.shape[0]):
            xyz_trans[i] = (R_ns @ xyz[i] + t_ns) * scale_ns
        ns_kpts[frame, :, :3] = xyz_trans
        ns_kpts[frame, :, 3] = mocap_kpts[frame, :, 3]


    ns_pts_dir = output_dir + 'keypoints3d_transformed/'
    if not os.path.exists(ns_pts_dir):
        os.makedirs(ns_pts_dir)

    for i in range(ns_kpts.shape[0]):
        kpts = ns_kpts[i, :, :]
        temp = {"id": mocap_kpt_ids[i], "keypoints3d": kpts.tolist()}
        fname = mocap_kpts_names[i]

        with open(ns_pts_dir + fname, 'w') as f:
            json.dump([temp], f)


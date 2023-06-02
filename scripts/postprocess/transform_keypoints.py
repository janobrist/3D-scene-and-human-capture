import sys
import os
import json
import numpy as np
import open3d as o3d
import colorsys
import argparse


def main(data_path, transform_path, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ns_transform_path = f"{transform_path}dataparser_transforms.json"
    with open(ns_transform_path, 'r') as file:
        ns_trans_params = json.load(file)


    R_ns = np.vstack(
        (ns_trans_params['transform'][0][:3], ns_trans_params['transform'][1][:3], ns_trans_params['transform'][2][:3]))
    t_ns = np.hstack(
        (ns_trans_params['transform'][0][3], ns_trans_params['transform'][1][3], ns_trans_params['transform'][2][3]))
    scale_ns = ns_trans_params['scale']

    mocap_kpts_names = os.listdir(data_path)
    mocap_kpts_names.sort()

    mocap_kpts = []
    mocap_kpt_ids = []

    for name in mocap_kpts_names:
        temp = read_json_as_dict(data_path + name)
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


    for i in range(ns_kpts.shape[0]):
        kpts = ns_kpts[i, :, :]
        temp = {"id": mocap_kpt_ids[i], "keypoints3d": kpts.tolist()}
        fname = mocap_kpts_names[i]

        with open(output_path + fname, 'w') as f:
            json.dump([temp], f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='demo/data/mocap/output/keypoints3d/',
                        help="path to keypoints")
    parser.add_argument('--transform', type=str, help="path to dataparser_transforms.json")
    parser.add_argument('--out', type=str, default='demo/data/mocap/output/transformed_keypoints/',
                        help="output directory of transformed keypoints")
    args = parser.parse_args()
    main(args.data, args.transform, args.out)



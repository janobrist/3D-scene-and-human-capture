import os
import numpy as np
import json
import argparse
from easymocap.mytools.camera_utils import write_extri, read_cameras


def read_json_as_dict(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


def calculate_limb_length(ktps_dir, kintree):
    ktps_names = os.listdir(ktps_dir)
    ktps_names.sort()
    kpts = []
    kpt_ids = []
    for name in ktps_names:
        temp = read_json_as_dict(ktps_dir + name)
        kpts.append(np.array(temp[0]['keypoints3d']))
        kpt_ids.append(temp[0]['id'])

    kpts = np.array(kpts)

    limb_length = np.linalg.norm(
        kpts[:, kintree[1:][:, 1], :3] - kpts[:, kintree[1:][:, 0], :3], axis=2, keepdims=True
    )
    return limb_length


def main(args):
    kintree = np.array([[1, 0], [2, 1], [3, 2], [4, 3], [5, 1], [6, 5], [7, 6], [8, 1], [9, 8], [10, 9], [11, 10], [12, 8], [13, 12], [14, 13]])

    # input arguments
    input_dir = args.input_dir
    output_dir = args.output_dir
    colmap_ktps_dir = args.colmap_ktps_dir
    easymocap_ktps_dir = args.easymocap_ktps_dir

    colmap_limb_length = calculate_limb_length(colmap_ktps_dir, kintree)
    easymocap_limb_length = calculate_limb_length(easymocap_ktps_dir, kintree)
    wcs_scale_factor = (np.mean(colmap_limb_length, axis=0) / np.mean(easymocap_limb_length, axis=0)).mean()

    # read extri parameters
    cams = read_cameras(path=input_dir)

    for key, val in cams.items():
        val['T'] = val['T'] / wcs_scale_factor

    # write new (scaled) extri parameters
    if not args.no_write:
        write_extri(os.path.join(output_dir, 'extri.yml'), cams)

    print('scale_factor = ', 1 / wcs_scale_factor)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Determine scaling factor to convert COLMAP to metric units")
    parser.add_argument("--input_dir", type=str, default="demo/data/mocap/motion/", help="Input directory of extri.yml")
    parser.add_argument("--output_dir", type=str, default="demo/data/mocap/motion_metric/", help="Output directory of extri.yml")
    parser.add_argument("--colmap_ktps_dir", type=str, default="demo/outputs/mocap/keypoints3d/", help="Colmap keypoints3d directory")
    parser.add_argument("--easymocap_ktps_dir", type=str, default="demo/outputs/mocap_native_calib/keypoints3d/", help="Easymocap keypoints3d directory")
    parser.add_argument("--no_write", action="store_true", help="Only print scaling factor")
    args = parser.parse_args()

    main(args)

import json
import numpy as np
import torch
import open3d as o3d
import argparse
import json
def main(data_path, scale, output_path):

    pcd = o3d.io.read_point_cloud(data_path)
    points = np.asarray(pcd.points)
    points_scaled = points * float(scale)

    scaled_pcd = o3d.geometry.PointCloud()
    scaled_pcd.points = o3d.utility.Vector3dVector(points_scaled)
    scaled_pcd.colors = pcd.colors
    o3d.io.write_point_cloud(f'{output_path}scaled_pcd.ply', scaled_pcd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='demo/exports/pcd/transformed_pcd.ply',
                        help="path to point cloud")
    parser.add_argument('--scale', type=float, help="scaling factor", default=1)
    parser.add_argument('--out', type=str, default='demo/reconstruction/pcd/',
                        help="output directory of all point-clouds")
    args = parser.parse_args()
    main(args.data, args.scale, args.out)
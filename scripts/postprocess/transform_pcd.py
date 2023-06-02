import json
import numpy as np
import torch
import open3d as o3d
import argparse
import json
def main(data_path, transform_path, output_path):
    path = f"{transform_path}dataparser_transforms.json"
    with open(path, 'r') as file:
        transformation = json.load(file)

    pcd = o3d.io.read_point_cloud(data_path)
    points = np.asarray(pcd.points)
    points_tensor = torch.tensor(points, dtype=torch.double)
    matrix = torch.eye(4, dtype=torch.double).unsqueeze(0).repeat(points_tensor.shape[0], 1, 1)
    matrix[:, :3, 3] = points_tensor

    matrix[..., :, :] /= transformation['scale']
    applied_transform1 = torch.tensor(transformation['transform'])
    inv_transform1 = torch.linalg.inv(
        torch.cat(
            (
                applied_transform1,
                torch.tensor([[0, 0, 0, 1]], dtype=torch.double, device=applied_transform1.device),
            ),
            0,
        )
    )
    applied_transform2 = torch.tensor([
            [
                0.0,
                1.0,
                0.0,
                0.0
            ],
            [
                1.0,
                0.0,
                0.0,
                0.0
            ],
            [
                -0.0,
                -0.0,
                -1.0,
                -0.0
            ]
        ])
    inv_transform2 = torch.linalg.inv(
        torch.cat(
            (
                applied_transform2,
                torch.tensor([[0, 0, 0, 1]], dtype=torch.double, device=applied_transform2.device),
            ),
            0,
        )
    )
    matrix = torch.einsum("ij,bjk->bik", inv_transform1, matrix)
    #matrix = torch.einsum("ij,bjk->bik", inv_transform2, matrix)
    array = matrix[..., :3, 3].numpy()
    transformed_pcd = o3d.geometry.PointCloud()
    transformed_pcd.points = o3d.utility.Vector3dVector(array)
    transformed_pcd.colors = pcd.colors
    o3d.io.write_point_cloud(f'{output_path}transformed_pcd.ply', transformed_pcd)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='demo/exports/pcd/point_cloud.ply',
                        help="path to keypoints")
    parser.add_argument('--transform', type=str, help="path to dataparser_transformation")
    parser.add_argument('--out', type=str, default='demo/exports/pcd/',
                        help="output directory of all point-clouds")
    args = parser.parse_args()
    main(args.data, args.transform, args.out)
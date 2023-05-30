import json
import numpy as np
import torch
import open3d as o3d

pcd = o3d.io.read_point_cloud('point_cloud.ply')
points = np.asarray(pcd.points)
points_tensor = torch.tensor(points, dtype=torch.double)
matrix = torch.eye(4, dtype=torch.double).unsqueeze(0).repeat(points_tensor.shape[0], 1, 1)
matrix[:, :3, 3] = points_tensor

scale = 0.14342626321373417
matrix[..., :, :] /= scale
applied_transform1 = torch.tensor([
        [
            -0.12332112342119217,
            0.12041550874710083,
            -0.9850340485572815,
            0.31251540780067444
        ],
        [
            0.9827098846435547,
            -0.12332112342119217,
            -0.13810555636882782,
            -0.26058244705200195
        ],
        [
            -0.13810555636882782,
            -0.9850340485572815,
            -0.10312539339065552,
            0.021094681695103645
        ]
    ],)
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
matrix = torch.einsum("ij,bjk->bik", inv_transform2, matrix)
array = matrix[..., :3, 3].numpy()
transformed_pcd = o3d.geometry.PointCloud()
transformed_pcd.points = o3d.utility.Vector3dVector(array)
transformed_pcd.colors = pcd.colors
o3d.io.write_point_cloud('transformed_pcd.ply', transformed_pcd)

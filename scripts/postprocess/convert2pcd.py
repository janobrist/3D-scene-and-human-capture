import json
import os
from typing import List, Tuple
import open3d as o3d
import numpy as np
from pathlib import Path
import math
import argparse


def get_json_files(directory_path: Path) -> List[str]:
    # Get a list of JSON files in the directory
    json_files: List[str] = [
        f for f in os.listdir(directory_path) if f.endswith(".json")
    ]

    # Sort the JSON files based on their numerical names (assuming frame numbers are used as file names)
    json_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    return json_files


def sample_points_on_cylinder(start_point, end_point, radius=0.005, num_points=50):
    # Calculate the direction vector and height of the cylinder
    direction = np.array(end_point) - np.array(start_point)
    height = np.linalg.norm(direction)
    axis = direction / height

    # Generate points along the height of the cylinder
    heights = np.linspace(0, height, num_points)

    # Generate points around the circumference of the cylinder
    angles = np.linspace(0, 2 * math.pi, num_points)

    # Generate the points on the cylinder
    points = []
    for h in heights:
        for angle in angles:
            x = start_point[0] + axis[0] * h
            y = start_point[1] + axis[1] * h
            z = start_point[2] + axis[2] * h

            point_on_circumference_x = x + radius * math.cos(angle)
            point_on_circumference_y = y + radius * math.sin(angle)
            point_on_circumference_z = z

            points.append(
                (
                    point_on_circumference_x,
                    point_on_circumference_y,
                    point_on_circumference_z,
                )
            )

    return points


def extend_pcd(skeleton_connections, keypoints, pcd):
    # now add another 2500 points to the point cloud to have a better mesh of the human
    for connection in skeleton_connections:
        start_point = keypoints[connection[0]]
        end_point = keypoints[connection[1]]
        if start_point != end_point:
            cylinder_points = sample_points_on_cylinder(start_point, end_point)
            pcd.points.extend(cylinder_points)


def main(data_path, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    json_files = get_json_files(data_path)

    # Create a list to store the keyframes for the animation

    # NOTE: The following code is specific to 25 point skeleton w/o hand or face model
    # Define the connections between keypoints for skeleton visualization
    skeleton_connections = [
        [0, 1],
        [1, 2],
        [1, 5],
        [5, 6],
        [6, 7],
        [2, 3],
        [3, 4],
        [1, 8],
        [8, 9],
        [8, 12],
        [9, 10],
        [10, 11],
        [11, 22],
        [22, 23],
        [11, 24],
        [12, 13],
        [13, 14],
        [14, 21],
        [19, 20],
        [14, 19],
        [0, 15],
        [0, 16],
        [15, 17],
        [16, 18],
    ]

    # Iterate over the JSON files
    counter = 0
    for json_file in json_files:
        # initialise a point cloud
        pcd = o3d.geometry.PointCloud()

        file_path: Path = data_path / json_file

        # Read keypoints data from the current JSON file
        with open(file_path, "r") as f:
            frame_data = json.load(f)

        # Set the current frame
        keypoints = []

        # Create cubes at the corresponding locations for the current frame
        for keypoint in frame_data[0]["keypoints3d"]:
            keypoints.append(keypoint[0:3])

        # add keypoints to pointcloud
        pcd.points = o3d.utility.Vector3dVector(keypoints)

        # add additional points to the point cloud to have a better mesh of the human
        extend_pcd(skeleton_connections, keypoints, pcd)

        pcd.paint_uniform_color([0, 0, 1])
        o3d.io.write_point_cloud(f"{output_path}{counter}.ply", pcd)
        counter += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='demo/data/mocap/output/keypoints3d/',
                        help="path to keypoints")
    parser.add_argument('--out', type=str, default='demo/data/mocap/output/pcd/',
                        help="output directory of all point-clouds")
    args = parser.parse_args()
    main(args.data, args.out)

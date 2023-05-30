import json
import os
import open3d as o3d
import numpy as np

if __name__ == '__main__':
    # Specify the directory path containing the JSON files
    directory_path = "data/final/mocap/output/keypoints3d_transformed"  # Replace with your directory path

    # Get a list of JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith(".json")]

    # Sort the JSON files based on their numerical names (assuming frame numbers are used as file names)
    json_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    output_path = 'data/final/mocap/output/pointcloud/'

    # Create a list to store the keyframes for the animation
    # Define the connections between keypoints for skeleton visualization
    skeleton_connections = [
        [0, 1], [1, 2], [1, 5], [5, 6], [6, 7], [2, 3], [3, 4],
        [1, 8], [8, 9], [8, 12], [9, 10], [10, 11], [11, 22], [22, 23],
        [11, 24], [12, 13], [13, 14], [14, 21], [19, 20],
        [14, 19], [0, 15], [0, 16], [15, 17], [16, 18]
    ]

    # Iterate over the JSON files
    counter = 0
    for json_file in json_files:
        file_path = os.path.join(directory_path, json_file)

        # Read keypoints data from the current JSON file
        with open(file_path, 'r') as f:
            frame_data = json.load(f)

        # Set the current frame
        frame_number = int(os.path.splitext(json_file)[0])
        keypoints = []

        # Create cubes at the corresponding locations for the current frame
        for keypoint in frame_data[0]['keypoints3d']:
            keypoints.append(keypoint[0:3])


        # Create the LineSet object
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(np.asarray(keypoints))
        line_set.lines = o3d.utility.Vector2iVector(np.asarray(skeleton_connections))
        line_set.paint_uniform_color([1, 0, 0])

        o3d.io.write_line_set(f"{output_path}pcd{counter}.ply", line_set)

        counter += 1


import subprocess
import os
import argparse

def extract_images_recon(video_path, output_folder, desired_fps):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Build the ffmpeg command
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f"fps={desired_fps}",
        os.path.join(output_folder, 'recon_%04d.jpg')
    ]

    # Run the ffmpeg command
    subprocess.call(command)
def extract_images_motion(video_path, output_folder):
    i = 1
    for file_name in os.listdir(video_path):
        path = os.path.join(video_path, file_name)

        command = [
            'ffmpeg',
            '-i', path,
            '-ss', str(0),
            '-vframes', '1',
            os.path.join(output_folder, 'motion_%04d.jpg' %i)
        ]
        i+=1

        # Run the ffmpeg command
        subprocess.call(command)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--reconstruction', type=str, default='demo/data/reconstruction/room.mov', help="path to video for reconstruction")
    parser.add_argument('--motion', type=str, default='demo/data/mocap/calibration/', help="path to folder with calibration videos for motion capture")
    parser.add_argument('--out', type=str, default='demo/data/reconstruction/img/', help="output directory of all images")
    parser.add_argument('--fps', type=float, default=3)
    args = parser.parse_args()

    extract_images_recon(args.reconstruction, args.out, args.fps)
    extract_images_motion(args.motion, args.out)
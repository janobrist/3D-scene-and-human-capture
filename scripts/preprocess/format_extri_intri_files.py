import os
import argparse
from easymocap.mytools.camera_utils import write_intri, write_extri, read_cameras

def main(input_dir, old_intri_name, old_extri_name, suffix, frame_numbers):
    # Checks
    assert os.path.exists(os.path.join(input_dir, old_intri_name))
    assert os.path.exists(os.path.join(input_dir, old_extri_name))

    # Main
    cams = read_cameras(path=input_dir)

    write_intri(os.path.join(input_dir, old_intri_name.split('.')[0] + suffix + '.yml'), cams)
    write_extri(os.path.join(input_dir, old_extri_name.split('.')[0] + suffix + '.yml'), cams)

    camnames = [list(cams.keys())[i - 1] for i in frame_numbers]
    cams_subset = {str(i + 1): cams[camnames[i]] for i in range(len(camnames))}

    write_intri(os.path.join(input_dir, 'intri.yml'), cams_subset)
    write_extri(os.path.join(input_dir, 'extri.yml'), cams_subset)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert COLMAP cameras to EasyMocap cameras')
    parser.add_argument('input_dir', type=str, help='Input directory')
    parser.add_argument('--old_intri_name', type=str, default='intri.yml', help='intri file name to convert')
    parser.add_argument('--old_extri_name', type=str, default='extri.yml', help='extri file name to convert')
    parser.add_argument('--suffix', type=str, default='_all_frames', help='Suffix to add to the converted files')
    parser.add_argument('--frame_numbers', nargs='+', type=int, default=[1, 2], help='COLMAP frame numbers to keep')

    args = parser.parse_args()

    main(args.input_dir, args.old_intri_name, args.old_extri_name, args.suffix, args.frame_numbers)

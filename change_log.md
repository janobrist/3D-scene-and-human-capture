# Commit Log 11/06/2023

## Edits
- directory changes : moved 1.mov and 2.mov to a folder called videos in demo/data/mocap/calibration (more compatible with easymocap pipeline)
- process_data.py : accommodate for new directory structure
- extract_video.py : added argument to specify video extension (previously didn't work for .mov)
- mv1p.py : added option to export only 3d kpts (no smpl)
- convert2bvh : set Pelvis to translation vector, set root to origin (plus z-factor), rotate around x-axis by 90 degrees to align with WCS conventions
- transform pcd : removed scaling factor from translation component, removed unused code (applied_transformation2)

## New Files
- format_extri_intri_files : creates new extri / intri yaml files using the output of read_colmap.py (in short, take first two frames and rename as "1" and "2" to match camera names in demo/data)
- prep_smpl_directories : shell file to make two new directories, copy images, and extri / intri files to re-run easymocap pipeline for scale factor estimation and smpl body fitting
- calc_metric_scale_factor.py : estimates limb length from native easy mocap pipeline (using calibration board) and from colmap / easymocap pipeline to calculate scale factor (from colmap -> metric units)
- scale_pcd : applies scaling factor to transformed_pcd.ply (-> metric units)
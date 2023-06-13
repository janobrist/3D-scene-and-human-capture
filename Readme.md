# Contents

- [About](https://github.com/janobrist/3D-scene-and-human-capture/edit/master/Readme.md#About)
- [Installation](https://github.com/janobrist/3D-scene-and-human-capture/edit/master/Readme.md#Installation)
- [Demo](https://github.com/janobrist/3D-scene-and-human-capture/edit/master/Readme.md#Demo)
- [FAQs](https://github.com/janobrist/3D-scene-and-human-capture/edit/master/Readme.md#FAQs)
- [References](https://github.com/janobrist/3D-scene-and-human-capture/edit/master/Readme.md#References)

# About

This repository contains a modified version of [EasyMocap](https://github.com/zju3dv/EasyMocap) [^EasyMocap] aimed at creating a seamless pipeline that correctly aligns captured human motion data in a 3D reconstructed model of the environment. For 3D reconstruction of the scene, [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) [^Tancik2023] is used. 
<div align="center">
    <img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/final.gif" width="100%">
    <br>
</div>

# Installation

## 1. Installing Nerfstudio

To install nerfstudio, follow the instructions in the [installation guidelines](https://github.com/nerfstudio-project/nerfstudio0/blob/main/docs/quickstart/installation.md#dependencies).

## 2. Installing OpenPose

Follow the installation guide from [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) [^Cao2019].

## 3. Installing EasyMocap

```bash
git clone git@github.com:janobrist/3D-scene-and-human-capture.git
```
See the detailed installation instructions in the [Documentation](https://chingswy.github.io/easymocap-public-doc/install/install.html) of EasyMocap.

# Demo

*Run the following pipeline to test all installations*

## 1. 3D Reconstruction

**Input:** Videos for Reconstruction and Mocap

**Output:** Camera parameters + sparse scene representation in [COLMAP](https://github.com/colmap/colmap) [^Schoenberger2016] coordinate system, Dense scene representation in Nerfstudio coordinate system

```bash
# Extract frames for pose estimation from 3D reconstruction and extrinsic videos
python scripts/preprocess/preprocess_data.py --reconstruction demo/data/reconstruction/room.mov --motion demo/data/mocap/calibration/ --out demo/data/reconstruction/img/ --fps 3


# Use COLMAP to determine camera extrinsic and instrinsic parameters:
conda activate nerfstudio
ns-process-data images --data demo/data/reconstruction/img/ --output-dir demo/data/reconstruction/ --matching-method exhaustive --num-downscales 1


# Use Nerfstudio to reconstruct 3D scene (warning: training/reconstrucion takes tens of minutes, up to 1 hour depending on resources):
ns-train nerfacto --data demo/data/reconstruction/ --output-dir demo/outputs/


# Export point cloud (specify config folder : {start_time}):
ns-export pointcloud --load-config demo/outputs/reconstruction/nerfacto/{start_time}/config.yml --output-dir demo/outputs/reconstruction/pcd/ --num-points 3000000 --remove-outliers True --estimate-normals False --use-bounding-box True --bounding-box-min -1 -1 -1 --bounding-box-max 1 1 1 

```

## 2. Generate Mocap 3D Keypoints 

**Input:** Videos for Mocap + COLMAP camera parameters

**Output:** 3D Keypoints in COLMAP coordinate system

*Note: EasyMocap uses OpenPose to detect 2D keypoints. If you encounter "out of memory" errors, reduce highres parameter below to value between 0 and 1 (see this [demo](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/01_demo.md#improving-memory-and-speed-but-decreasing-accuracy) and this [FAQ](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/b1cb2b69cf8c4c288921e48c37f339a64db26f58/doc/05_faq.md#out-of-memory-error) for more information).*

```bash
# Use OpenPose to detect 2D keypoints (specify path to OpePose, adjust highres as necessary):
conda activate easymocap
python scripts/preprocess/extract_video.py demo/data/mocap/motion/ --openpose {path_to_openpose}/ --highres 1


# Extract camera intrinsics and extrinsics from COLMAP output:
python apps/calibration/read_colmap.py demo/data/reconstruction/colmap/sparse/0 .bin --out demo/data/mocap/motion/
python scripts/preprocess/format_extri_intri_files.py demo/data/mocap/motion/ --frame_numbers 1 2


# Use EasyMocap to generate 3D keypoints:
python apps/demo/mv1p.py demo/data/mocap/motion/ --out demo/outputs/mocap/ --vis_det --vis_repro --body body25 --kpts_only

```

## 3. Align Nerfstudio and COLMAP Coordinate Systems

*Note: We generated 3D keypoints in the COLMAP coordinate system (which is already aligned with the Sparse scene reconstruction). To align the Dense reconstruction, either transform the nerfstudio ply to the COLMAP system (required for generating SMPL in next step) or transform the 3D keypoints to the nerfstudio coordinate system.*

**Input:** Dense point cloud (nerfstudio coordinate system) --OR-- 3D keypoints (COLMAP coordinate system)

**Output:** Dense point cloud (COLMAP coordinate system) --OR-- 3D keypoints (nerfstudio coordinate system)

```bash
# Dense point cloud transformation: nerfstudio -> COLMAP
python scripts/postprocess/transform_pcd.py --data demo/outputs/reconstruction/pcd/point_cloud.ply --transform demo/outputs/reconstruction/nerfacto/{start_time}/ --out demo/outputs/reconstruction/pcd/


# 3D keypoints transformation: COLMAP -> nerfstudio
python scripts/postprocess/transform_keypoints.py --data demo/outputs/mocap/keypoints3d/ --transform demo/outputs/reconstruction/nerfacto/{start_time}/ --out demo/outputs/mocap/transformed_keypoints/


# Visualize the 3D keypoints as a skeleton (convert to point clouds):
## if dense point cloud was transformed above
python scripts/postprocess/convert2pcd.py --data demo/data/mocap/output/transformed_keypoints3d/ --out demo/outputs/mocap/pcd/

## else if 3D keypoints were transformed
python scripts/postprocess/convert2pcd.py --data demo/outputs/mocap/keypoints3d/ --out demo/outputs/mocap/pcd/

```

**Tips for Visualization:** use blender/animation.blend [^FlipBook] to visualize the point clouds (copy all point clouds into FlipBookCollection, hide all in FlipBookCollection, adjust number of frames to amount of point clouds). For optimal visualization of the 3D reconstructed point-cloud we used the Blender point cloud visualizer add-on [^addon].*

## 4. Export SMPL Body Parameters and Blender Mocap Data (.bvh)

**Disclaimer: Requires additional downloads and up to 2 GB of disc space**

**Foreword:** EasyMocap trained its model for fitting SMPL parameters on data with real metric units. Since COLMAP and nerfstudio use Structure from Motion (SfM), their coordinate systems do not have real units. This extention of the pipeline is one method for estimating and applying a scaling factor to the COLMAP camera parameters in order to improve the results of EasyMocap's SMPL body reconstruction. The scaling factor is calculated as the ratio between the average limb length of the human in the COLMAP coordinate system and the average limb length of the human in the coordinate system generated using EasyMocap's native camera calibration procedure (detecting a chessboard of known size).

### 4.1. Additional Requirements

- Follow [this](https://github.com/zju3dv/EasyMocap/blob/master/doc/installation.md#01-smpl-models) guide to download SMPL model and reproduce folder structure
    - For this demo, structure should follow: data > smlpx > smlp > SMLP_NEUTRAL.pkl
- (Optional for .bvh) Follow [this](https://github.com/zju3dv/EasyMocap/blob/master/doc/02_output.md#export-to-bvh-format) guide, download SMPL_maya from [SMPL website](https://smpl.is.tue.mpg.de/download.php), and install [Blender-2.79a](https://download.blender.org/release/Blender2.79/)

### 4.2.1. Calculate Camera Extrinsics (in metric units) using Calibration Chessboard

**Input:** Calibration videos

**Output:** Extrinsic camera parameters for 3D keypoint generation in "EasyMocap native" coordinate system

```bash
# Copy camera intrinsics generated by COLMAP
cp demo/data/mocap/motion/intri.yml demo/data/mocap/calibration

# extract all images from calibration video and detect chessboard corners
python scripts/preprocess/extract_video.py demo/data/mocap/calibration --no2d --vid_ext ".mov"
python apps/calibration/detect_chessboard.py demo/data/mocap/calibration --out demo/data/mocap/calibration/chessboard_detections --pattern 8,6 --grid 0.120

# (optional) check / edit detection results using EasyMocap application
python apps/annotation/annot_calib.py demo/data/mocap/calibration --mode chessboard --pattern 8,6 --annot chessboard

# extract extrinsics
python apps/calibration/calib_extri.py demo/data/mocap/calibration --intri demo/data/mocap/calibration/intri.yml

```

### 4.2.2. Generate 3D keypoints ("EasyMocap native")

**Input:** Mocap images, EasyMocap native camera extrinsics

**Output:** 3D keypoints

```bash
# run the following shell script to set up new directories and copy necessary files
chmod +x scripts/postprocess/prep_smpl_directories.sh
./scripts/postprocess/prep_smpl_directories.sh

# Run OpenPose for 2D keypoint detection
python scripts/preprocess/extract_video.py demo/data/mocap/motion_native_calib/ --openpose {path_to_openpose}/ --highres 1

# Extract 3D keypoints
python apps/demo/mv1p.py demo/data/mocap/motion_native_calib --out demo/outputs/mocap_native_calib --vis_det --vis_repro --body body25 --kpts_only

```

### 4.2.3. Estimate COLMAP scaling factor, Scale COLMAP Extrinsics, Re-generate 3D keypoints

**Input:** 3D keypoints (EasyMocap Native --and-- COLMAP)

**Output:** scaled 3D keypoints (COLMAP aligned to metric system, saved in `demo/data/mocap/motion_metric/`)

```bash
# Caluclate COLMAP scaling factor (scaling factor will be printed, copy and save for later) and scale COLMAP extrinsics
python scripts/postprocess/calc_metric_scale_factor.py --input_dir demo/data/mocap/motion/ --output_dir demo/data/mocap/motion_metric/ --colmap_ktps_dir demo/outputs/mocap/keypoints3d/ --easymocap_ktps_dir demo/outputs/mocap_native_calib/keypoints3d/

# Run OpenPose to regenerate 2D keypoints
python scripts/preprocess/extract_video.py demo/data/mocap/motion_metric/ --openpose {path_to_openpose}/ --highres 1

# Generate 3D keypoints
python apps/demo/mv1p.py demo/data/mocap/motion_metric --out demo/outputs/mocap_metric --vis_det --vis_repro --body body25 --kpts_only

```

### 4.2.4. Visualize Keypoints, Generate SMPL, Transform Point Cloud

**Input:** 3D keypoints (COLMAP aligned to metric)

**Output:** point clouds (.ply), motion capture data (.bvh), SMPL body parameters (.json)

```bash
# to export keypoints as point clouds
python scripts/postprocess/convert2pcd.py --data demo/outputs/mocap_metric/keypoints3d/ --out demo/outputs/mocap_metric/pcd/

# to only generate smpl body parameters
python apps/demo/smpl_from_keypoints.py demo/data/mocap/motion_metric  --skel3d demo/outputs/mocap_metric/keypoints3d --out demo/outputs/mocap_metric/smpl

# to generate smpl body parameters AND overlay body model on original mocap images
python apps/demo/mv1p.py demo/data/mocap/motion_metric --out demo/outputs/mocap_metric --vis_det --vis_repro --body body25 --model smpl --gender neutral --vis_smpl

# to export smpl as .bvh (see additional requirements above)
{path_to_blender}/blender -b -t 12 -P scripts/postprocess/convert2bvh.py -- demo/outputs/mocap_metric/smpl --o demo/outputs/mocap_metric/

# to scale Dense point cloud, you must have
## -- point cloud in COLMAP coordinates (see section 3)
## -- scale factor from previous step (can re-print if need be, see below)
python scripts/postprocess/scale_pcd.py --data demo/outputs/reconstruction/pcd/transformed_pcd.ply --scale {scale_factor} --out demo/outputs/reconstruction/pcd/

# print out scale_factor
python scripts/postprocess/calc_metric_scale_factor.py --input_dir demo/data/mocap/motion/ --output_dir demo/data/mocap/motion_metric/ --colmap_ktps_dir demo/outputs/mocap/keypoints3d/ --easymocap_ktps_dir demo/outputs/mocap_native_calib/keypoints3d/ --no_write

```

**Tips for Visualization:** .bvh file will only produce skeleton (bones). To fit smpl body, do the following:
- import SMLP maya (.fbx) into scene and scale xyz by 100 (0.01 -> 1)
- move mesh outside of armature parent, then delete armature
- rotate mesh by 90 degrees about X-axis
- select mesh, shift-select .bvh armature, ctrl-P -> Armature Deform

### 4.3. Results

<img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/dynamic.gif" width="49%"/> <img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/skeleton.gif" width="49%"/>

# FAQs

### 1. Can I run OpenPose indentently from EasyMocap?

EasyMocap uses OpenPose to estimate 2D joint locations (keypoints), which it calls in `scripts/preprocess/preprocess/extract_video.py`. This function supports additionaly flags which are not included in the Demo, namely `--handface` for hand and face keypoint generation (currently separate calls to each functionality not supported) and `--render` to generate images with a 2D skeleton of the keypoint overlaid. Both functions increase computational resources significantly. 

OpenPose has many more options available natively to improve its detections results (i.e. undistorting images before detection). To run OpenPose independently, call the function `convert_from_openpose()` in `scripts/preprocess/preprocess/extract_video.py` to format the keypoints for use in the EasyMocap pipeline.

### 2. Can I use more than 2 cameras for capturing human motion?

This pipeline supports any number of cameras (>=2), so long as they are time-synced. Include all videos in the same directory named `videos`, i.e. `demo/data/mocap/motion/videos`. Each camera should have a separate video with no human in the scene for the generatation of its extrinsic parameters. If using COLMAP to estimate these parameters, specify the index (`--frame_number`) of the images corresponding to each camera when calling  `scripts/preprocess/format_extri_intri_files.py` (see section 2 in the Demo above). This will properly format the `intri.yml` and `extri.yml` files required for the EasyMocap pipeline. 

### 3. Can I detect more than one person in the scene?

Yes. Due to limited computational resources, we were unable to test multi-person detection, but EasyMocap includes a separate function to triangulate 2D keypoints in scenes with multiple people. See `apps/demo/mvmp.py`.

### 4. Can I use SMPL-H/SMLP-X or other body models?

Yes. See [this](https://chingswy.github.io/easymocap-public-doc/install/install_smpl.html) for a list of supported models. Using SMPL-H/SMLP-X requires the generation of additional keypoints from OpenPose (see FAQ 1 above). Replace the flag `--body25` with `--bodyhand` or `--bodyhandface` (SMPL-H and SMPL-X, respectivitely) when calling the function `apps/demo/mv1p.py` to recreate the SMPL model. We were unable to try different body models due to limited computational resources. 

### 5. Are there any other useful functions not included in the demo?

Yes! The documentation for EasyMocap does not explain all of the functions it contains. ...


### 

# References

[^Tancik2023]: Matthew Tancik et al. Nerfstudio: A modular framework for neural radiance field development. arXiv preprint arXiv:2302.04264, 2023

[^Easymocap]: Easymocap - make human motion capture easier. Github, 2021

[^addon]: Blender point cloud visualizer 2.0+. Github, 2023

[^FlipBook]: Importing Static Point Cloud vs Animated Point Coud into Blender Geometry Nodes. YouTube, 2022

[^Cao2019]: Zhe Cao et al. Openpose: Realtime multi-person 2d poseestimation using part affinity fields, 2019

[^Schoenberger2016]: Johannes Lutz Schoenberger and Jan-Michael Frahm. Structure-from-Motion Revisited. In Conference on Computer Vision and Pattern Recognition (CVPR), 2016

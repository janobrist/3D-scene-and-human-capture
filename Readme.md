# About
This repository contains a modified version of [EasyMocap](https://github.com/zju3dv/EasyMocap) aimed at creating a seamless pipeline that correctly aligns captured human motion data in a 3D reconstructed model of the environment. For 3D reconstruction of the scene, [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) is used. 
<div align="center">
    <img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/final.gif" width="100%">
    <br>
</div>

# Installation
## 1. Installing Nerfstudio
To install nerfstudio, follow the instructions in the [installation guidelines](https://github.com/nerfstudio-project/nerfstudio0/blob/main/docs/quickstart/installation.md#dependencies).
## 2. Installing OpenPose
Follow the installation guide from [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose).
## 3. Installing EasyMocap
```bash
git clone git@github.com:janobrist/3D-scene-and-human-capture.git

```
See the detailed installation instructions in the [Documentation](https://chingswy.github.io/easymocap-public-doc/install/install.html) of EasyMocap.
# Demo
Test all installations by using the following pipeline:

Extract frames for pose estimation from 3D reconstruction and extrinsic videos:
```bash
python scripts/preprocess/preprocess_data.py --reconstruction demo/data/reconstruction/room.mov --motion demo/data/mocap/calibration/ --out demo/data/reconstruction/img/ --fps 3

```
Use [COLMAP](https://github.com/colmap/colmap) to determine camera extrinsic and instrinsic parameters:
```bash
conda activate nerfstudio

```
```bash
ns-process-data images --data demo/data/reconstruction/img/ --output-dir demo/data/reconstruction/ --matching-method exhaustive --num-downscales 1

```
Use Nerfstudio to reconstruct 3D scene and export point-cloud:
```bash
ns-train nerfacto --data demo/data/reconstruction/ --output-dir demo/outputs/

```
Export point cloud:
```bash
ns-export pointcloud --load-config demo/outputs/reconstruction/nerfacto/{start_time}/config.yml --output-dir demo/exports/pcd/ --num-points 3000000 --remove-outliers True --estimate-normals False --use-bounding-box True --bounding-box-min -1 -1 -1 --bounding-box-max 1 1 1 

```
Use OpenPose to detect 2D keypoints (if you encounter out of memory error, reduce highres parameter):
```bash
conda activate easymocap

```
```bash
python scripts/preprocess/extract_video.py demo/data/mocap/motion/ --openpose {path_to_openpose}/ --highres 1

```
Create camera extrinsics from sparse colmap reconstruction:
```bash
python apps/calibration/read_colmap.py demo/data/reconstruction/colmap/sparse/0 .bin --out demo/data/mocap/motion/

```
Use EasyMocap to generate 3D keypoints and SMPL body model:
```bash
python apps/demo/mv1p.py demo/data/mocap/motion/ --out demo/outputs/mocap/ --vis_det --vis_repro --sub_vis 1 2 --body body25 --model smpl --gender neutral --vis_smpl

```
either convert 3D keypoints or point cloud to align both outputs:
```bash
python scripts/postprocess/transform_keypoints.py --data demo/outputs/mocap/keypoints3d/ --transform demo/outputs/reconstruction/nerfacto/{start_time}/ --out demo/outputs/mocap/transformed_keypoints/

```
```bash
python scripts/postprocess/transform_pcd.py --data demo/outputs/reconstruction/pcd/point_cloud.ply --transform demo/outputs/reconstruction/nerfacto/{start_time}/ --out demo/outputs/pcd/

```

Create .bvh file from SMPL body parameters (requires Blender 2.79):
```bash
"{path_to_blender}/blender.exe" -b -t 12 -P scripts/postprocess/convert2bvh.py -- demo/outputs/mocap/smpl/ --o demo/outputs/mocap/blender/

```

or visualize the 3D keypoints as a skeleton by converting them to point clouds (use --data demo/data/mocap/output/transformed_keypoints3d/ if keypoints were transformed before):

```bash
python scripts/postprocess/convert2pcd.py --data demo/outputs/mocap/keypoints3d/ --out demo/outputs/mocap/pcd/

```
use blender/animation.blend to visualize the point clouds (copy all point clouds into FlipBookCollection, hide all in FlipBookCollection, adjust number of frames to amount of point clouds).

<img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/dynamic.gif" width="49%"/> <img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/skeleton.gif" width="49%"/>

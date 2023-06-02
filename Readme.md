# About
This repository contains a modified version of [EasyMocap](https://github.com/zju3dv/EasyMocap) aimed at creating a seamless pipeline that correctly aligns captured human motion data in a 3D reconstructed model of the environment. For the 3D reconstruction, [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) is used. 
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
cd demo
ns-process-data images --data data/reconstruction/img/ --output-dir data/reconstruction/ --matching-method exhaustive --num-downscales 1.0

```
Use Nerfstudio to reconstruct 3D scene and export point-cloud:
```bash
ns-train nerfacto --data data/reconstruction/
ns-export pointcloud --load-config outputs/unnamed/nerfacto/{start_time}/config.yml --output-dir exports/pcd/ --num-points 3000000 --remove-outliers True --estimate-normals False --use-bounding-box True --bounding-box-min -1 -1 -1 --bounding-box-max 1 1 1 

```
Use OpenPose to detect 2D keypoints (if you encounter memory issues reduce --highres parameter):
```bash
conda activate easymocap
scripts/preprocess/extract_video.py data/mocap/ --openpose openpose/ --highres 1

```
Create camera extrinsics from sparse colmap reconstruction:
```bash
python apps/calibration/read_colmap.py data/final/recon/colmap/sparse/0 .bin

```
Use EasyMocap to generate 3D keypoints and SMPL body model:
```bash
python apps/demo/mv1p.py data/mocap/ --out data/mocap/output/ --vis_det --vis_repro --sub_vis 1 2 --body body25 --model smpl --gender neutral --vis_smpl

```
Create .bvh file from SMPL body parameters (requires Blender 2.79):
```bash
"{path_to_blender}/blender.exe" -b -t 12 -P scripts/postprocess/convert2bvh.py -- data/mocap/output/smpl/ --o data/mocap/output/blender/

```

or visualize the 3D keypoints as a skeleton by converting them to point clouds:

```bash
python convert2pcd.py --input path --output path

```
use animation.blend to visualize the point clouds (copy them in the collection and adjust number of frames).

<img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/dynamic.gif" width="49%"/> <img src="https://github.com/janobrist/3D-scene-and-human-capture/blob/master/demo/results/skeleton.gif" width="49%"/>

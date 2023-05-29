# About
This repository consists of a forked version of [EasyMocap](https://github.com/zju3dv/EasyMocap) with the goal to establish a pipeline that features the combination of 3D reconstruction of static scenes and capuring human motion in the same scene. For the 3D reconstruction, [Nerfstudio](https://github.com/nerfstudio-project/nerfstudio) is used. 

# Installation
## 1. Installing Nerfstudio
To install nerfstudio, follow the instructions in the [installation guidelines](https://github.com/nerfstudio-project/nerfstudio0/blob/main/docs/quickstart/installation.md#dependencies).
## 2. Installing OpenPose
Follow the installation guide from [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose).
## 3. Installing EasyMocap
```bash
conda create --name easymocap -y python=3.9
conda activate easymocap
python -m pip install --upgrade pip
```
```bash
git clone
cd 
```
# Demo
Extract frames for pose estimation from 3D reconstruction and extrinsic videos.
```bash
python preprocessing.py --reconstruction-video path.. --cam-left path... --cam-right...

```
Use [COLMAP](https://github.com/colmap/colmap) to determine camera extrinsic and instrinsic parameters.
```bash
conda activate nerfstudio
ns-process-data images --data data/test/custom4/ --output-dir data/test/ --matching-method exhaustive --num-downscales 1.0

```
Use Nerfstudio to reconstruct 3D scene and export point-cloud.
```bash
ns-train nerfacto --data path
ns-export pointcloud --load-config outputs\unnamed\nerfacto\2023-05-26_082508/config.yml --output-dir exports/pcd/ --num-points 3000000 --remove-outliers True --estimate-normals False --use-bounding-box True --bounding-box-min -1.2 -1 -1 --bounding-box-max 1 1 1 

```
Use OpenOse to detect 2D keypoints.
```bash
scripts/preprocess/extract_video.py data/final/mocap/motion/ --openpose openpose/ --highres 0.7

```
Use EasyMocap to generate 3D keypoints and SMPL body model.
```bash
python apps/calibration/read_colmap.py data/final/recon/colmap/sparse/0 .bin
python apps/demo/mv1p.py test/ --out "test/output/smplx" --vis_det --vis_repro --sub_vis 1 2 --body body25 --model smpl --gender neutral --vis_smpl

python apps/demo/smpl_from_keypoints.py data/final/mocap/  --skel3d data/final/mocap/output//keypoints3d/ --out data/final/mocap/output/smpl/
"C:\Program Files\Blender Foundation\Blender\blender.exe" -b -t 12 -P scripts/postprocess/convert2bvh.py -- test/smpl_model --o test/output2/


ffmpeg -i reconstruction2.mp4 -r 3 test/frame%d.jpg
ffmpeg -i input.mp4 -vf scale=320:240,setsar=1:1 output.mp4
```




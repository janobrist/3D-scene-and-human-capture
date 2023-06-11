#!/bin/sh

mkdir demo/data/mocap/motion_native_calib
cp -r demo/data/mocap/motion/images demo/data/mocap/motion_native_calib
cp demo/data/mocap/calibration/intri.yml  demo/data/mocap/motion_native_calib
cp demo/data/mocap/calibration/extri.yml  demo/data/mocap/motion_native_calib

mkdir demo/data/mocap/motion_metric
cp -r demo/data/mocap/motion/images demo/data/mocap/motion_metric
cp demo/data/mocap/calibration/intri.yml  demo/data/mocap/motion_metric

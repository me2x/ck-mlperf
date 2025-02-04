# Collective Knowledge workflows for MLPerf

[![compatibility](https://github.com/ctuning/ck-guide-images/blob/master/ck-compatible.svg)](https://github.com/ctuning/ck)
[![automation](https://github.com/ctuning/ck-guide-images/blob/master/ck-artifact-automated-and-reusable.svg)](http://cTuning.org/ae)

[![DOI](https://zenodo.org/badge/149591037.svg)](https://zenodo.org/badge/latestdoi/149591037)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Linux/MacOS: [![Travis Build Status](https://travis-ci.org/ctuning/ck-mlperf.svg?branch=master)](https://travis-ci.org/ctuning/ck-mlperf)

## MLPerf Inference v0.5

| Task | Model | Owner | Contributors | Implementation | Environment (need more testing) | CK workflow |
|-|-|-|-|-|-|-|
| Object Classification | MobileNet     | dividiti  | dividiti  | [TFLite](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/tflite) | Linux, Android (Windows, Mac) | yes |
|                       |               |           | dividiti  | [TF (C++)](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/tf-cpp) | Linux, Android (Windows, Mac) | yes |
|                       |               |           | dividiti  | [TF (Python)](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/tf-py) | Linux (Windows, Mac) | yes |
|                       |               |           | dividiti, NVIDIA, Microsoft | [ONNX](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/onnx) | Linux, Mac (Windows) | yes |
|                       |               |           | dividiti, Arm               | [ArmNN](https://github.com/arm-software/armnn-mlperf) | Linux (Android) | yes |
|                       | ResNet        | Microsoft | Microsoft | [ONNX](https://github.com/mlperf/inference/blob/master/cloud/image_classification) | Linux (?) | no |
|                       |               |           | Microsoft | [TF (Python)](https://github.com/mlperf/inference/blob/master/cloud/image_classification) | Linux (?) | no |
|                       |               |           | dividiti  | [TFLite](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/tflite#install-the-resnet-model) | Linux, Android (Windows, Mac) | yes |
|                       |               |           | dividiti  | [TF (C++)](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/tf-cpp#install-the-resnet-model) | Linux, Android (Windows, Mac) | yes |
|                       |               |           | dividiti  | [ONNX](https://github.com/mlperf/inference/tree/master/edge/object_classification/mobilenets/onnx#install-the-resnet-model) | Linux, Mac (Windows) | yes |
|                       |               |           | dividiti, Arm | [ArmNN](https://github.com/arm-software/armnn-mlperf) | Linux (Android) | yes |
| Object Detection      | SSD-MobileNet | dividiti  | dividiti  | [TFLite](https://github.com/mlperf/inference/tree/master/edge/object_detection/ssd_mobilenet/tflite) | Linux (Android, Windows, Mac) | yes |
|                       |               |           | dividiti, Habana | [TF (Python)](https://github.com/mlperf/inference/tree/master/edge/object_detection/ssd_mobilenet/tf-py) | Linux (?) | yes |
|                       |               |           | Facebook  | [PyTorch](https://github.com/mlperf/inference/tree/master/edge/object_detection/ssd_mobilenet/pytorch) | Linux (?) | no |
|                       | SSD-ResNet    | Habana    | Habana, NVIDIA    | [PyTorch](https://github.com/mlperf/inference/tree/master/cloud/single_stage_detector/pytorch) | Linux (?) | no |
|                       |               |           | GM, Google, dividiti | TF | (?) | **coming soon!** |
| Machine Translation   | GNMT          | Intel     | Intel     | [TF (Python)](https://github.com/mlperf/inference/blob/master/cloud/translation/gnmt/tensorflow) | Linux (?) | no |
|                       |               |           | Intel     | [PyTorch](https://github.com/mlperf/inference/blob/master/cloud/translation/gnmt/pytorch) | Linux (?) | no |

**NB:** We generally acknowledge Google for making many pretrained [TF models](https://github.com/tensorflow/models) available (e.g. for [Object Detection](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md)).

## MLPerf Training v0.6
**TODO**

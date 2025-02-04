#!/usr/bin/env python3

import json
import time
import os
import shutil
import numpy as np
import onnxruntime as rt

## Model properties:
#
MODEL_PATH              = os.environ['CK_ENV_ONNX_MODEL_ONNX_FILEPATH']
INPUT_LAYER_NAME        = os.environ['CK_ENV_ONNX_MODEL_INPUT_LAYER_NAME']
OUTPUT_LAYER_NAME       = os.environ['CK_ENV_ONNX_MODEL_OUTPUT_LAYER_NAME']
MODEL_DATA_LAYOUT       = os.environ['ML_MODEL_DATA_LAYOUT']
MODEL_IMAGE_HEIGHT      = int(os.environ['CK_ENV_ONNX_MODEL_IMAGE_HEIGHT'])
MODEL_IMAGE_WIDTH       = int(os.environ['CK_ENV_ONNX_MODEL_IMAGE_WIDTH'])
LABELS_PATH             = os.environ['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT']

## Image normalization:
#
MODEL_NORMALIZE_DATA    = os.getenv("CK_ENV_ONNX_MODEL_NORMALIZE_DATA") in ('YES', 'yes', 'ON', 'on', '1')
SUBTRACT_MEAN           = os.getenv("CK_ENV_ONNX_MODEL_SUBTRACT_MEAN") in ('YES', 'yes', 'ON', 'on', '1')
GIVEN_CHANNEL_MEANS     = os.getenv("ML_MODEL_GIVEN_CHANNEL_MEANS", '')
if GIVEN_CHANNEL_MEANS:
    GIVEN_CHANNEL_MEANS = np.array(GIVEN_CHANNEL_MEANS.split(' '), dtype=np.float32)

## Input image properties:
#
IMAGE_DIR               = os.getenv('CK_ENV_DATASET_IMAGENET_PREPROCESSED_DIR')
IMAGE_LIST_FILE         = os.path.join(IMAGE_DIR, os.getenv('CK_ENV_DATASET_IMAGENET_PREPROCESSED_SUBSET_FOF'))
IMAGE_DATA_TYPE         = np.dtype( os.getenv('CK_ENV_DATASET_IMAGENET_PREPROCESSED_DATA_TYPE', 'uint8') )

## Writing the results out:
#
RESULTS_DIR             = os.getenv('CK_RESULTS_DIR')
FULL_REPORT             = os.getenv('CK_SILENT_MODE', '0') in ('NO', 'no', 'OFF', 'off', '0')

## Processing in batches:
#
BATCH_SIZE              = int(os.getenv('CK_BATCH_SIZE', 1))
BATCH_COUNT             = int(os.getenv('CK_BATCH_COUNT', 1))
CPU_THREADS             = int(os.getenv('CK_HOST_CPU_NUMBER_OF_PROCESSORS',0))


def load_preprocessed_batch(image_list, image_index):
    batch_data = []
    for _ in range(BATCH_SIZE):
        img_file = os.path.join(IMAGE_DIR, image_list[image_index])
        img = np.fromfile(img_file, IMAGE_DATA_TYPE)
        img = img.reshape((MODEL_IMAGE_HEIGHT, MODEL_IMAGE_WIDTH, 3))

        if IMAGE_DATA_TYPE != 'float32':
            img = img.astype(np.float32)

            # Normalize
            if MODEL_NORMALIZE_DATA:
                img = img/127.5 - 1.0

            # Subtract mean value
            if SUBTRACT_MEAN:
                if len(GIVEN_CHANNEL_MEANS):
                    img -= GIVEN_CHANNEL_MEANS
                else:
                    img -= np.mean(img)

        # Add img to batch
        batch_data.append( [img] )
        image_index += 1

    nhwc_data = np.concatenate(batch_data, axis=0)

    if MODEL_DATA_LAYOUT == 'NHWC':
        #print(nhwc_data.shape)
        return nhwc_data, image_index
    else:
        nchw_data = nhwc_data.transpose(0,3,1,2)
        #print(nchw_data.shape)
        return nchw_data, image_index


def load_labels(labels_filepath):
    my_labels = []
    input_file = open(labels_filepath, 'r')
    for l in input_file:
        my_labels.append(l.strip())
    return my_labels


def main():
    global INPUT_LAYER_NAME
    global OUTPUT_LAYER_NAME
    global BATCH_SIZE
    global BATCH_COUNT

    print('Images dir: ' + IMAGE_DIR)
    print('Image list file: ' + IMAGE_LIST_FILE)
    print('Model image height: {}'.format(MODEL_IMAGE_HEIGHT))
    print('Model image width: {}'.format(MODEL_IMAGE_WIDTH))
    print('Batch size: {}'.format(BATCH_SIZE))
    print('Batch count: {}'.format(BATCH_COUNT))
    print('Results dir: ' + RESULTS_DIR);
    print('Normalize: {}'.format(MODEL_NORMALIZE_DATA))
    print('Subtract mean: {}'.format(SUBTRACT_MEAN))
    print('Per-channel means to subtract: {}'.format(GIVEN_CHANNEL_MEANS))

    setup_time_begin = time.time()

    # Load preprocessed image filenames:
    with open(IMAGE_LIST_FILE, 'r') as f:
        image_list = [ s.strip() for s in f ]

    # Cleanup results directory
    if os.path.isdir(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
    os.mkdir(RESULTS_DIR)

    # Load the ONNX model from file
    sess_options = rt.SessionOptions()
    if CPU_THREADS > 0:
        sess_options.enable_sequential_execution = False
        sess_options.session_thread_pool_size = CPU_THREADS
    sess = rt.InferenceSession(MODEL_PATH,sess_options)


    input_layer_names   = [ x.name for x in sess.get_inputs() ]     # FIXME: check that INPUT_LAYER_NAME belongs to this list
    INPUT_LAYER_NAME    = INPUT_LAYER_NAME or input_layer_names[0]

    output_layer_names  = [ x.name for x in sess.get_outputs() ]    # FIXME: check that OUTPUT_LAYER_NAME belongs to this list
    OUTPUT_LAYER_NAME   = OUTPUT_LAYER_NAME or output_layer_names[0]

    model_input_shape   = sess.get_inputs()[0].shape

    model_classes       = sess.get_outputs()[0].shape[1]
    labels              = load_labels(LABELS_PATH)
    bg_class_offset     = model_classes-len(labels)  # 1 means the labels represent classes 1..1000 and the background class 0 has to be skipped

    if MODEL_DATA_LAYOUT == 'NHWC':
        (samples, height, width, channels) = model_input_shape
    else:
        (samples, channels, height, width) = model_input_shape

    print("Data layout: {}".format(MODEL_DATA_LAYOUT) )
    print("Input layers: {}".format([ str(x) for x in sess.get_inputs()]))
    print("Output layers: {}".format([ str(x) for x in sess.get_outputs()]))
    print("Input layer name: " + INPUT_LAYER_NAME)
    print("Expected input shape: {}".format(model_input_shape))
    print("Output layer name: " + OUTPUT_LAYER_NAME)
    print("Background/unlabelled classes to skip: {}".format(bg_class_offset))
    print("")

    setup_time = time.time() - setup_time_begin

    # Run batched mode
    test_time_begin = time.time()
    image_index = 0
    total_load_time = 0
    total_classification_time = 0
    first_classification_time = 0
    images_loaded = 0

    for batch_index in range(BATCH_COUNT):
        batch_number = batch_index+1
        if FULL_REPORT or (batch_number % 10 == 0):
            print("\nBatch {} of {}".format(batch_number, BATCH_COUNT))
      
        begin_time = time.time()
        batch_data, image_index = load_preprocessed_batch(image_list, image_index)

        load_time = time.time() - begin_time
        total_load_time += load_time
        images_loaded += BATCH_SIZE
        if FULL_REPORT:
            print("Batch loaded in %fs" % (load_time))

        # Classify batch
        begin_time = time.time()
        batch_results = sess.run([OUTPUT_LAYER_NAME], {INPUT_LAYER_NAME: batch_data})[0]
        classification_time = time.time() - begin_time
        if FULL_REPORT:
            print("Batch classified in %fs" % (classification_time))

        total_classification_time += classification_time
        # Remember first batch prediction time
        if batch_index == 0:
            first_classification_time = classification_time

        # Process results
        for index_in_batch in range(BATCH_SIZE):
            softmax_vector = batch_results[index_in_batch][bg_class_offset:]    # skipping the background class on the left (if present)
            global_index = batch_index * BATCH_SIZE + index_in_batch
            res_file = os.path.join(RESULTS_DIR, image_list[global_index])
            with open(res_file + '.txt', 'w') as f:
                for prob in softmax_vector:
                    f.write('{}\n'.format(prob))
            
    test_time = time.time() - test_time_begin
 
    if BATCH_COUNT > 1:
        avg_classification_time = (total_classification_time - first_classification_time) / (images_loaded - BATCH_SIZE)
    else:
        avg_classification_time = total_classification_time / images_loaded

    avg_load_time = total_load_time / images_loaded

    # Store benchmarking results:
    output_dict = {
        'setup_time_s': setup_time,
        'test_time_s': test_time,
        'images_load_time_total_s': total_load_time,
        'images_load_time_avg_s': avg_load_time,
        'prediction_time_total_s': total_classification_time,
        'prediction_time_avg_s': avg_classification_time,

        'avg_time_ms': avg_classification_time * 1000,
        'avg_fps': 1.0 / avg_classification_time,
        'batch_time_ms': avg_classification_time * 1000 * BATCH_SIZE,
        'batch_size': BATCH_SIZE,
    }
    with open('tmp-ck-timer.json', 'w') as out_file:
        json.dump(output_dict, out_file, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()

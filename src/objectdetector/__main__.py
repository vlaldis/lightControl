import time
from datetime import datetime
from os import path

import numpy as np
import cv2
import argparse

import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
 
from object_detection.utils import label_map_util
 
from src.core.redisclient import RedisClient

parser = argparse.ArgumentParser(description="Analyze frames and estimate object type using tensorflow.")
parser.add_argument('-r', '--redis-server', metavar='server:port', type=str, default='redis:6379',
                    help="URL to redis server. Default 'redis:6379'.")
parser.add_argument('-s', '--session', metavar='session-name', type=str, default='default',
                    help="Session identification. Frames will be stored in redis under 'session-name:key'."
                    "Default 'default'.")
parser.add_argument('-d', '--debug', action='store_true', help="Write debug messages to console.")
parser.add_argument("-m", "--frozen-model", type=str, default="/frozen_inference_graph.pb", help="Pre-trained model to load")
parser.add_argument("-l", "--label-map", type=str, default="label_map.pbtxt", help="Path to COCO label map file") 
parser.add_argument("-t", "--threshold", type=float, default=0.5, help="minimum detection threshold to use")
parser.add_argument("--frame-delay", type=int, default=1, help="Delay between frames in seconds. Default 1.")

args = parser.parse_args()
print("Arguments:")
print(args)


def debug(text):
    if args.debug:
        print("{}: {}".format(datetime.utcnow(), text))


def file_not_found(file):
    print("Can not find file '{}'.".format(file))


def load_model(path_to_model):
    debug("Loading model '{}' ...".format(path_to_model))
    if not path.exists(path_to_model):
        file_not_found(path_to_model)
        exit(1)

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.compat.v1.GraphDef()
        with tf.compat.v2.io.gfile.GFile(path_to_model, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    debug("Model '{}' loaded successfully".format(path_to_model))

    return detection_graph


def load_labels(path_to_labels):
    debug("Loading label map '{}' ...".format(path_to_labels))
    if not path.exists(path_to_labels):
        file_not_found(path_to_labels)
        exit(1)

    label_map = label_map_util.load_labelmap(path_to_labels)
    max_num_classes = max([item.id for item in label_map.item])
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=max_num_classes, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    debug("Label map '{}' loaded successfully".format(path_to_labels))

    return category_index


def nextFrameId(redis):
    return redis.getLastFrameId()
    

def next_frame(redis, frameId):
    frameBytes = redis.getFrame(frameId)
    if frameBytes is None:
        return None

    frame = cv2.imdecode(frameBytes, flags=1)
    debug("Got new frame. Frame id:{:d}".format(frameId))

    return frame


def main():
    detection_graph = load_model(args.frozen_model)
    category_index = load_labels(args.label_map)
    
    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis.")

    previousFrameId = -1
    try:
        with detection_graph.as_default():
            with tf.Session(graph=detection_graph) as sess:
                while True:
                    frameId = nextFrameId(redis)
                    if frameId is None or frameId == previousFrameId:
                        debug("New frame is not available.")
                        time.sleep(args.frame_delay)
                        continue
                    
                    previousFrameId = frameId
                    frame = next_frame(redis, frameId)

                    if frame is None:
                        debug("Can not read frame {}. Skipping..." % frameId)
                        continue

                    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                    frame_expanded = np.expand_dims(frame, axis=0)
                    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                    scores = detection_graph.get_tensor_by_name('detection_scores:0')
                    classes = detection_graph.get_tensor_by_name('detection_classes:0')
                    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                    
                    # Actual detection.
                    (boxes, scores, classes, num_detections) = sess.run(
                        [boxes, scores, classes, num_detections],
                        feed_dict={image_tensor: frame_expanded})
                    
                    detections_count = np.squeeze(scores)
                    debug("Detected {} objects in image".format(len(detections_count[detections_count>args.threshold])))
                    
                    # Squeeze arrays
                    scores = np.trim_zeros(np.squeeze(scores),'b').tolist()
                    lastIndex = len(scores)
                    classes = np.squeeze(classes)[0:lastIndex].astype(np.int32)
                    categories = [category_index[idx]['name'] for idx in classes]
                    boxes = np.squeeze(boxes)[0:lastIndex, :].tolist()

                    detections = {i: {"class":categories[i], "score":scores[i], "box":boxes[i]} for i in range(0, len(scores))}
                    redis.addDetections(frameId, detections)
    except Exception as e:
        print(str(e))
    finally:
        debug("Exiting...")


if __name__ == '__main__':
    main()

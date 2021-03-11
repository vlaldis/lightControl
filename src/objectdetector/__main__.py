import time
from datetime import datetime
from os import path

import numpy as np
import cv2
import argparse
 
import tensorflow as tf

from src.core.labels import category_index
from src.core.redisclient import RedisClient
from src.core.videostream import VideoStream

parser = argparse.ArgumentParser(description="Analyze frames and estimate object type using tensorflow.")
parser.add_argument('-i', '--input', metavar='http://my.video.source.com/', type=str, default='0',
                    help="Source can be id of connected web camera or stream URL. Default '0' (internal web camera id).")
parser.add_argument('--delay', metavar='N.N', type=float, default=1.0,
                    help="Delay between two images. No need to have all captured frames. Sample: value=2.0 will add image each 2 seconds."
                    " Default 1.0 .")
parser.add_argument('-r', '--redis-server', metavar='server:port', type=str, default='redis:6379',
                    help="URL to redis server. Default 'redis:6379'.")
parser.add_argument('-s', '--session', metavar='session-name', type=str, default='default',
                    help="Session identification. Frames will be stored in redis under 'session-name:key'."
                    "Default 'default'.")
parser.add_argument('-d', '--debug', action='store_true', help="Write debug messages to console.")
parser.add_argument("-m", "--frozen-model", type=str, default="/frozen_inference_graph.pb", help="Pre-trained model to load")
# parser.add_argument("-l", "--label-map", type=str, default="label_map.pbtxt", help="Path to COCO label map file") 
parser.add_argument("-t", "--threshold", type=float, default=0.5, help="minimum detection threshold to use")


args = parser.parse_args()
print("Arguments:")
print(args, flush=True)


def debug(text):
    if args.debug:
        print("{}: {}".format(datetime.utcnow(), text), flush=True)


def file_not_found(file):
    print("Can not find file '{}'.".format(file))


def main():
    input = int(args.input) if args.input.isnumeric() else args.input
    stream = VideoStream(input)
    debug("Successfully connected to Stream '{}'.".format(args.input))

    saved_model = tf.saved_model.load('C:/projects/lightControl/deploy/networks/ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8/saved_model')

    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis.")

    lastid = redis.getLastFrameId()
    frameId = int(lastid) if lastid else 0
    try:
        while True:
            frame = stream.read()
            if frame is None:
                debug("Got empty image")
                time.sleep(args.delay)
                continue
            
            frameBytes = cv2.imencode(".jpg", frame)[1].tostring()
            redis.addFrame(frameId, frameBytes)
            debug("New frame added to Redis. Frame id: {:d}".format(frameId))

            # frame_expanded = np.expand_dims(frame, axis=0)
            frame_expanded = np.array(frame)
            
            input_tensor = tf.convert_to_tensor(frame_expanded)

            # The model expects a batch of images, so add an axis with `tf.newaxis`.
            input_tensor = input_tensor[tf.newaxis, ...]

            # input_tensor = np.expand_dims(image_np, 0)
            detections = saved_model(input_tensor)
            print(1)

            # All outputs are batches tensors.
            # Convert to numpy arrays, and take index [0] to remove the batch dimension.
            # We're only interested in the first num_detections.
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                        for key, value in detections.items()}
            detections['num_detections'] = num_detections

            # detection_classes should be ints.
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)
            
            boxes = detections["detection_boxes"]
            scores = detections["detection_scores"]
            classes = detections["detection_classes"]
            
            detections_count = np.squeeze(scores)
            debug("Detected {} objects in image".format(len(detections_count[detections_count>args.threshold])))
            
            # Squeeze arrays
            scores = np.trim_zeros(np.squeeze(scores),'b').tolist()
            lastIndex = len(scores)
            classes = np.squeeze(classes)[0:lastIndex]
            categories = [category_index[idx]['name'] for idx in classes]
            boxes = np.squeeze(boxes)[0:lastIndex, :].tolist()

            detections = {i: {"class":categories[i], "score":scores[i], "box":boxes[i]} for i in range(0, len(scores)) if scores[i]>args.threshold}
            redis.addDetections(frameId, detections)

            frameId = frameId + 1
            time.sleep(args.delay)
    except Exception as e:
        print(str(e))
    finally:
        debug("Exiting...")


if __name__ == '__main__':
    main()

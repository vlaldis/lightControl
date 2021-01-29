import time
from datetime import datetime
import cv2
import argparse
import numpy as np

from src.core.redisclient import RedisClient

parser = argparse.ArgumentParser(description="Visualize data from redis.")
parser.add_argument('-r', '--redis-server', metavar='server:port', type=str, default='redis:6379',
                    help="URL to redis server. Default 'redis:6379'.")
parser.add_argument('-s', '--session', metavar='session-name', type=str, default='default',
                    help="Session identification. Frames will be stored in redis under 'session-name:key'."
                    "The same will be used for ZeroMQ. Default 'default'.")
parser.add_argument('-d', '--debug', action='store_true', help="Write debug messages to console.")
parser.add_argument('--raw', action='store_true', help="Show clean frames without detections."
                    "Otherwise frames with detected objects will be displayed.")

args = parser.parse_args()
print("Arguments:")
print(args)

font = cv2.FONT_HERSHEY_SIMPLEX
red = (125, 0, 0)


def debug(text):
    if args.debug:
        print("{}: {}".format(datetime.utcnow(), text))


def next_frame(redis):
    frameId = redis.getLastFrameId()
    if frameId is None:
        return None        
    
    frameBytes = redis.getFrame(frameId)
    if frameBytes is None:
        return None

    frame = cv2.imdecode(frameBytes, flags=1)
    debug("Got new frame. Frame id:{}".format(frameId))

    return frame


def visualize(frame, detections):
    frame = cv2.imdecode(frame, flags=1)
    height = frame.shape[0]
    width = frame.shape[1]

    for detection in detections:
        data = detections[detection]
        text = "{} {:.0f}%".format(data['class'], data['score']*100)
        box = data['box'] * np.array([height, width, height, width])
        box = box.astype(int)
        frame = cv2.rectangle(frame, (box[1], box[0]), (box[3], box[2]), red, 3)
        frame = cv2.putText(frame, text, (box[1], box[0]-5), font, 0.8, red, 2, cv2.LINE_AA) 
   
    return frame


def next_detection(redis):
    detectionId = redis.getLastDetectionId()

    if detectionId is None:
        return None
    
    frame, detections = redis.getDetections(detectionId)
    
    if frame is None or detections is None:
        return None

    debug("Got new detection. Detection id: {}".format(detectionId))
    return visualize(frame, detections)


def main():
    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis.")

    try:
        while True:
            frame = next_frame(redis) if args.raw else next_detection(redis)

            if frame is None:
                debug("New image is not available.")
                time.sleep(5)
                continue
            
            cv2.imshow('object detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    except Exception as e:
        print(str(e))
    finally:
        debug("Exiting...")


if __name__ == '__main__':
    main()

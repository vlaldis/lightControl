import time
from datetime import datetime
import cv2
import argparse

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

def next_detection(redis):
    detectionId = redis.getLastDetectionId()

    if detectionId is None:
        return None        
    
    detectionBytes = redis.getDetection(detectionId)
    if detectionBytes is None:
        return None

    detection = cv2.imdecode(detectionBytes, flags=1)
    debug("Got new detection. Detection id:{}".format(detectionId))

    return detection


def main():
    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis.")

    try:
        while True:
            if args.raw:
                detection = next_frame(redis)
            else:
                detection = next_detection(redis)

            if detection is None:
                debug("New image is not available.")
                time.sleep(5)
                continue

            cv2.imshow('object detection', detection)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    except Exception as e:
        print(str(e))
    finally:
        redis.close()
        # zmq.close()
        debug("Exiting...")


if __name__ == '__main__':
    main()

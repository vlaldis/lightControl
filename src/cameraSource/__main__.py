import time
from datetime import datetime

import cv2
import argparse

from redisclient import RedisClient

parser = argparse.ArgumentParser(description="Parse video input to separate frames.")
parser.add_argument('-i', '--input', metavar='http://my.video.source.com/', type=str, default='0',
                    help="Source can be id of connected web camera or stream URL. Default '0' (internal web camera id).")
parser.add_argument('-f', '--fps', metavar='N', type=int, default=1,
                    help="Framerate per second. Default 1.")
parser.add_argument('-r', '--redis-server', metavar='server:port', type=str, default='redis:6379',
                    help="URL to redis server. Default 'redis:6379'.")
parser.add_argument('-s', '--session', metavar='session-name', type=str, default='default',
                    help="Session identification. Frames will be stored in redis under session-name:key. Default 'default'.")
parser.add_argument('-d', '--debug', action='store_true', help="Write debug messages to console.")

args = parser.parse_args()

print("Arguments:")
print(args, flush=True)

def debug(text):
    if args.debug:
        print("{}: {}".format(datetime.utcnow(), text), flush=True)

if __name__ == '__main__':
    capture = cv2.VideoCapture(args.input)
    debug("Successfully connected to Camera '{}'.".format(args.input))

    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis '{}'.".format(args.redis_server))

    frameId = redis.getLastFrameId()

    try:
        while capture.isOpened():
            ret, frame = capture.read()
            debug("Got frame.")
            frameBytes = cv2.imencode(".jpg", frame)[1].tostring()
            redis.addFrame(frameId, frameBytes)
            debug("New frame added to Redis. Frame id:{}".format(frameId))

            frameId = frameId + 1
            time.sleep(1/args.fps)
    finally:
        capture.release()
        redis.close()
        debug("Exiting...")

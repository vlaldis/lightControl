import time
from datetime import datetime
from threading import Thread

import cv2
import argparse

from src.core.redisclient import RedisClient

parser = argparse.ArgumentParser(description="Parse video input to separate frames.")
parser.add_argument('-i', '--input', metavar='http://my.video.source.com/', type=str, default='0',
                    help="Source can be id of connected web camera or stream URL. Default '0' (internal web camera id).")
parser.add_argument('--delay', metavar='N.N', type=float, default=1.0,
                    help="Delay between two images. No need to have all captured frames. Sample: value=2.0 will add image each 2 seconds."
                    " Default 1.0 .")
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


class VideoStream:
    def __init__(self, stream):
        self.stream = stream
        self.capture = None
        self.frame = None
        self.canceled = False
        self.thread = Thread(target=self.readStream, args=())
        self.thread.daemon = True
        self.thread.start()

    def connect(self):
        if self.canceled:
            return

        if self.capture:
            self.capture.release()

        self.capture = cv2.VideoCapture(self.stream)
        if not self.capture.isOpened():
            print("Can not open camera")
            time.sleep(1)

    def readStream(self):
        while True:
            if self.capture is None or not self.capture.isOpened():
                debug("Stream is closed. Conecting ...")
                self.connect()
            else:
                (self.status, self.frame) = self.capture.read()

    def read(self):
        return self.frame

    def release(self):
        self.canceled = True
        self.capture.release()
        

def main():
    input = int(args.input) if args.input.isnumeric() else args.input
    stream = VideoStream(input)
    debug("Successfully connected to Stream '{}'.".format(args.input))

    redis = RedisClient(args.redis_server)
    debug("Successfully connected to Redis '{}'.".format(args.redis_server))

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
            frameId = frameId + 1

            time.sleep(args.delay)
    except Exception as e:
        print(str(e))
    finally:
        stream.release()
        debug("Exiting...")


if __name__ == '__main__':
    main()

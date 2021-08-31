import time
from datetime import datetime
from threading import Thread

import argparse
# import Jetson.GPIO as GPIO

from src.core.redisclient import RedisClient
from nightTime import NightTime

parser = argparse.ArgumentParser(description="Turn on lights if person/car/bicycle is detected.")
parser.add_argument('-r', '--redis-server', metavar='server:port', type=str, default='redis:6379',
                    help="URL to redis server. Default 'redis:6379'.")
parser.add_argument('-s', '--session', metavar='session-name', type=str, default='default',
                    help="Session identification. Frames will be stored in redis under 'session-name:key'."
                    "Default 'default'.")
parser.add_argument('-d', '--debug', action='store_true', help="Write debug messages to console.")
parser.add_argument('-p', '--period', type=int, default=5, help="For how long should be the lights on.")
parser.add_argument('-c', '--control-pin', metavar='N', type=int, default=-1,
                    help='Pin for light control. Value specifies output GPIO. \
                        If set to High, lights are on. Default -1 (do not use).')

args = parser.parse_args()
print("Arguments:")
print(args)

# GPIO.setmode(GPIO.BOARD)
# pin = args.control_pin
# if pin >= 0:
#     GPIO.setup(pin, GPIO.OUT)

# objects of interes
OOI = ['person', 'car', 'bicycle']
hasRelevantObject = lambda detections: detections is not None and 0 < len([v for _, v in detections.items() if v['class'] in OOI])


def debug(text):
    if args.debug:
        print("{}: {}".format(datetime.utcnow(), text))


def next_detection(redis):
    detectionId = redis.getLastDetectionId()

    if detectionId is None:
        return None
    
    _, detections = redis.getDetections(detectionId)
    
    return detections

class Timer:
    def __init__(self, defaultPeriodInSeconds, gpio):
        self.defaultPeriod = defaultPeriodInSeconds
        self.currentPeriod = self.defaultPeriod
        self.gpio = gpio
        self.running = False
        self.thread = None
        # if pin >= 0:
        #    GPIO.setup(pin, GPIO.OUT)

    def run(self):
        debug("Lights on!")
        #GPIO.output(pin, GPIO.HIGH)
        while self.running and self.currentPeriod:
            time.sleep(1)
            self.currentPeriod -= 1
        #GPIO.output(pin, GPIO.LOW)
        debug("Lights off!")

    def start(self):
        self.running = True
        self.currentPeriod = self.defaultPeriod

        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self.run, args=())
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.running = False
        self.currentPeriod = 0
        if self.thread:
            self.thread.join()            
        pass


def main():
    timer = Timer(args.period, args.control_pin)
    redis = RedisClient(args.redis_server)
    nightTime = NightTime()
    hour = 3600 # seconds

    debug("Successfully connected to Redis.")

    try:
        while True:
            if not nightTime.isNight():
                secondsTillNight = nightTime.SecondsTillNight()
                delay = secondsTillNight if secondsTillNight < hour  else hour
                debug("Hey, it's a day! I'll take a nap for {0} seconds ...".format(delay))
                time.sleep(delay)
                continue

            detections = next_detection(redis)

            if detections is None or len(detections) == 0:
                time.sleep(10)
                continue
            
            if hasRelevantObject(detections):
                timer.start()

    except Exception as e:
        print(str(e))
    finally:
        debug("Exiting...")        
        timer.stop()


if __name__ == '__main__':
    main()

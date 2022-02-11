import time
from threading import Thread

import cv2

class VideoStream:
    max_empty_frames = 5

    def __init__(self, stream):
        self.stream = stream
        self.capture = None
        self.frame = None
        self.canceled = False
        self.watchdog = 0
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
            print("Can not open stream")
            time.sleep(1)
        else:
            print("Successfully connected to Stream '{}'.".format(self.stream))
            self.tick()

    def readStream(self):
        try:
            while True:
                if self.canceled:
                    break

                self.watchdog = self.watchdog + 1

                if self.shouldReconnectStream():
                    print("Stream is closed. Connecting ...")
                    self.connect()
                else:
                    (self.status, self.frame) = self.capture.read()
                    
                    if self.frame is not None:
                        self.tick() 

        except Exception as ex:
            print("Error in video stream thread: {}".format(str(ex)))

    def read(self):
        return self.frame

    def release(self):
        self.canceled = True
        self.capture.release()

    def shouldReconnectStream(self):
        return self.capture is None or not self.capture.isOpened() or self.watchdog == self.max_empty_frames

    def tick(self):
        self.watchdog = 0
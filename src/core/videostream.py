import time
from threading import Thread

import cv2

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
                print("Stream is closed. Conecting ...")
                self.connect()
            else:
                (self.status, self.frame) = self.capture.read()

    def read(self):
        return self.frame

    def release(self):
        self.canceled = True
        self.capture.release()

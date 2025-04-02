from threading import Thread
import cv2
from picamera2 import Picamera2
import time

class VideoStream:
    def __init__(self, resolution=(640, 480), framerate=30):
        self.frame = None
        self.stopped = False

        self.camera = Picamera2()
        config = self.camera.create_video_configuration(main={"size": resolution, "format": "RGB888"})
        self.camera.configure(config)
        self.camera.set_controls({"FrameRate": framerate})
        self.camera.start()
        time.sleep(2)

    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            self.frame = self.camera.capture_array()

    def read(self):
        while self.frame is None:
            time.sleep(0.01)
        return cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)

    def stop(self):
        self.stopped = True
        time.sleep(0.1)
        self.camera.stop()

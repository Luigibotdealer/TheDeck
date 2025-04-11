from threading import Thread
import cv2
from picamera2 import Picamera2
import time

class VideoStream:
    """Camera object using Picamera2"""

    def __init__(self, resolution=(640, 480), framerate=30):
        self.frame = None  # Stores the latest frame
        self.stopped = False

        # Initialize Picamera2
        self.camera = Picamera2()

        # Create camera configuration
        config = self.camera.create_video_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.camera.configure(config)

        # ✅ Lock frame rate via frame duration
        frame_duration_us = int(1_000_000 / framerate)  # e.g., 10 FPS = 100000 us
        self.camera.set_controls({"FrameDurationLimits": (frame_duration_us, frame_duration_us)})

        self.camera.start()
        time.sleep(2)  # Allow camera to warm up

    def start(self):
        """Start the thread to read frames from the video stream"""
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        """Continuously capture frames in a separate thread"""
        while not self.stopped:
            self.frame = self.camera.capture_array()

    def read(self):
        """Return the most recent frame"""
        return self.frame

    def stop(self):
        """Stop the camera stream"""
        self.stopped = True
        self.camera.stop()
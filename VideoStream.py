from threading import Thread
import cv2
from picamera2 import Picamera2
import time

class VideoStream:
    """Camera object using Picamera2"""

    def __init__(self, resolution=(640, 480), framerate=30):
        self.frame = None
        self.stopped = False
        self.thread = None

        try:
            self.camera = Picamera2()

            config = self.camera.create_video_configuration(
                main={"size": resolution, "format": "RGB888"}
            )
            self.camera.configure(config)

            frame_duration_us = int(1_000_000 / framerate)
            self.camera.set_controls({
                "FrameDurationLimits": (frame_duration_us, frame_duration_us)
            })

            self.camera.start()
            time.sleep(2)  # warm-up

            self.camera.set_controls({
                "AeEnable": False,
                "AwbEnable": False,
                "AnalogueGain": 1.0,
                "ExposureTime": 10000,
            })

        except Exception as e:
            print("[VideoStream] ❌ Error during camera init:", e)
            self.camera = None
            raise RuntimeError("Could not initialize camera.") from e

    def start(self):
        if self.thread and self.thread.is_alive():
            print("[VideoStream] Already running.")
            return self

        self.stopped = False
        self.thread = Thread(target=self.update, daemon=True)
        self.thread.start()
        return self

    def update(self):
        while not self.stopped:
            try:
                self.frame = self.camera.capture_array()
            except Exception as e:
                print("[VideoStream] ⚠️ Capture failed:", e)
                self.frame = None
                break

    def read(self):
        if self.frame is None:
            print("[VideoStream] ⚠️ No frame available yet.")
        return self.frame

    def stop(self):
        if not self.stopped:
            self.stopped = True
            # Allow the capture thread to finish
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1)

            # Properly release the camera
            if self.camera:
                try:
                    self.camera.stop()      # halt streaming
                except Exception as e:
                    print("[VideoStream] stop() warning:", e)

                try:
                    self.camera.close()     # ✨ fully release libcamera session
                except Exception as e:
                    print("[VideoStream] close() warning:", e)


    def __del__(self):
        self.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

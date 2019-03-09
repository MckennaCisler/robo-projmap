from freenect2 import Device, FrameType
import time
import atexit

class Kinect:
    def __init__(self):
        self.device = Device()
        self.running = False
        self.latest_color_frame = None
        self.latest_depth_frame = None
        atexit.register(self.device.close)

    # live frame calls

    def start(self, live=False):
        """ Starts the kinect streaming. Set live to true if you'll want every frame """
        if live:
            self.device.start()
        else:
            self.device.start(frame_listener=self._frame_listener)
        self.running = True
    
    def stop(self):
        self.device.stop()
        self.running = False

    def _frame_listener(self, frametype, frame):
        if frametype == FrameType.Color:
            self.latest_color_frame = frame
        elif frametype == FrameType.Depth:
            self.latest_depth_frame = frame
        elif frametype == FrameType.Ir:
            pass # nothing yet
    
    def get_current_color_frame(self):
        while self.latest_color_frame is None:
            time.sleep(0.001)
        return self._convert_frame(self.latest_color_frame)
    
    def get_current_depth_frame(self):
        while self.latest_depth_frame is None:
            time.sleep(0.001)
        return self._convert_frame(self.latest_depth_frame)

    # single frame calls

    def get_single_color_frame(self):
        return self._get_single_frame(FrameType.Color)

    def get_single_depth_frame(self):
        return self._get_single_frame(FrameType.Depth)

    def _get_single_frame(self, frametype):
        with self.device.running():
            for type_, frame1 in self.device:
                if type_ is frametype:
                    break
        return self._convert_frame(frame1)

    def _convert_frame(self, frame):
        img = frame.to_array().copy()
        img = img[:, ::-1]
        img[..., :3] = img[..., 2::-1] # bgrx -> rgbx
        return img

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import cv2

    k = Kinect()
    k.start() # for speed
    imgs = []

    print("capturing images")
    for i in range(100):
        imgs.append(k.get_current_color_frame())
    k.stop()

    print("displaying images")
    for i in range(len(imgs)):
        print("display image %d" % i)
        cv2.imshow('img', imgs[i][..., 2::-1])
        cv2.waitKey(10)


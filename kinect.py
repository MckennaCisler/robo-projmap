from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
import time
import atexit
import numpy as np

# try:
#     from pylibfreenect2 import OpenGLPacketPipeline
#     pipeline = OpenGLPacketPipeline()
# except:
try:
    from pylibfreenect2 import OpenCLPacketPipeline
    pipeline = OpenCLPacketPipeline()
except:
    from pylibfreenect2 import CpuPacketPipeline
    pipeline = CpuPacketPipeline()
print("Kinect packet pipeline:", type(pipeline).__name__)

class Kinect:
    def __init__(self, kinect_num=0):
        self.fn = Freenect2()
        self.serial = None
        self.device = None
        self.listener = None
        self.registration = None

        self._frames = None # frames cache so that the user can use them before we free them
        self._bigdepth = Frame(1920, 1082, 4) # malloc'd
        self._undistorted = Frame(512, 424, 4)
        self._registered = Frame(512, 424, 4)
        self._color_dump = Frame(1920, 1080, 4)

        num_devices = self.fn.enumerateDevices()
        if num_devices <= kinect_num:
            raise ConnectionError("No Kinect device at index %d" % kinect_num)

        self.serial = self.fn.getDeviceSerialNumber(kinect_num)
        self.device = self.fn.openDevice(self.serial, pipeline=pipeline)

        self.listener = SyncMultiFrameListener(FrameType.Color | FrameType.Depth)

        # Register listeners
        self.device.setColorFrameListener(self.listener)
        self.device.setIrAndDepthFrameListener(self.listener)

    def close(self):
        if self.device:
            self.device.close()

    def start(self):
        if self.device:
            self.device.start()
            self.registration = Registration(self.device.getIrCameraParams(),
                        self.device.getColorCameraParams())
            return self # for convenience
        else:
            raise ConnectionError("Connection to Kinect wasn't established")
    
    def stop(self):
        if self.device:
            self.device.stop()

    ### If copy is False for these functoins, make sure to call release_frames
    ### when you're done with the returned frame ###

    def get_current_color_frame(self, copy=True):
        self._frames = self.listener.waitForNewFrame()
        ret = self._convert_color_frame(self._frames["color"], copy=copy)
        if copy:
            self.release_frames()
        return ret
    
    def get_current_depth_frame(self, copy=True):
        self._frames = self.listener.waitForNewFrame()
        if copy:
            ret = self._frames["depth"].asarray().copy()
            self.release_frames()
        else:
            ret = self._frames["depth"].asarray()
        return ret

    def get_current_rgbd_frame(self, copy=True):
        self._frames = self.listener.waitForNewFrame()

        self.registration.apply(self._frames["color"], self._frames["depth"], 
            self._undistorted, self._registered, bigdepth=self._bigdepth)

        color = self._convert_color_frame(self._frames["color"], copy=copy)
        depth = self._convert_bigdepth_frame(self._bigdepth, copy=copy)
        if copy:
            self.release_frames()
        return color, depth

    def get_current_bigdepth_frame(self, copy=True):
        self._frames = self.listener.waitForNewFrame()

        self.registration.apply(self._frames["color"], self._frames["depth"], 
            self._undistorted, self._registered, bigdepth=self._bigdepth)

        depth = self._convert_bigdepth_frame(self._bigdepth, copy=copy)
        if copy:
            self.release_frames()
        return depth

    def release_frames(self):
        self.listener.release(self._frames)

    # single frame calls

    def get_single_color_frame(self):
        self.start()
        ret = self.get_current_color_frame()
        self.stop()
        return ret

    def get_single_depth_frame(self):
        self.start()
        ret = self.get_current_depth_frame()
        self.stop()
        return ret

    def _convert_bigdepth_frame(self, frame, copy=True):
        if copy:
            d = self._bigdepth.asarray(np.float32).copy()
        else:
            d = self._bigdepth.asarray(np.float32)
        return d[1:-1,::-1]

    def _convert_color_frame(self, frame, copy=True):
        if copy:
            img = frame.asarray().copy()
        else:
            img = frame.asarray()
        img = img[:, ::-1]
        img[..., :3] = img[..., 2::-1] # bgrx -> rgbx
        return img

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import cv2

    SINGLE_DEMO = True

    k = Kinect()
    k.start() # for speed

    if SINGLE_DEMO:
        rgb, d = k.get_current_rgbd_frame()
        print(d.shape, rgb.shape)
        k.stop()
        cv2.imshow('d', d*0.001)
        cv2.waitKey(0)
        cv2.imshow('rgb', rgb[..., 2::-1])
        cv2.waitKey(0)
        
    else:
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


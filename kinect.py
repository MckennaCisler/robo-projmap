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
            del(self.latest_color_frame)
            self.latest_color_frame = frame
        elif frametype == FrameType.Depth:
            del(self.latest_depth_frame)
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

    def get_current_rgbd_frame(self):
        while self.latest_color_frame is None or self.latest_depth_frame is None:
            time.sleep(0.001)
        depth_small, rgb_small, depth_big = self.device.registration.apply(\
            self.latest_color_frame, self.latest_depth_frame, with_big_depth=True)
        color = self._convert_frame(self.latest_color_frame)
        depth = depth_big.to_array()[1:-1,::-1]
        del(depth_small)
        del(rgb_small)
        del(depth_big)
        return color, depth

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
        img = frame.to_array()
        img = img[:, ::-1]
        img[..., :3] = img[..., 2::-1] # bgrx -> rgbx
        return img

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import cv2

    k = Kinect()
    k.start() # for speed
    imgs = []

    rgb, d = k.get_current_rgbd_frame()
    print(d.shape, rgb.shape)
    k.stop()
    cv2.imshow('d', d*0.001)
    cv2.waitKey(0)
    cv2.imshow('rgb', rgb[..., 2::-1])
    cv2.waitKey(0)

    # print("capturing images")
    # for i in range(100):
    #     imgs.append(k.get_current_color_frame())
    # k.stop()

    # print("displaying images")
    # for i in range(len(imgs)):
    #     print("display image %d" % i)
    #     cv2.imshow('img', imgs[i][..., 2::-1])
    #     cv2.waitKey(10)


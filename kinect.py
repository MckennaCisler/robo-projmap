from freenect2 import Device, FrameType

class Kinect:
    def __init__(self):
        self.device = Device()
        # self.device.start()

    def __del__(self):
        self.device.close()

    def start(self):
        self.device.start()
    
    def stop(self):
        self.device.stop()
    
    def get_color_frame(self):
        with self.device.running():
            for type_, frame1 in self.device:
                if type_ is FrameType.Color:
                    break
        return frame1.to_array().copy()[:, ::-1]

    def get_depth_frame(self):
        with self.device.running():
            for type_, frame1 in self.device:
                if type_ is FrameType.Depth:
                    break
        return frame1.to_array().copy()[:, ::-1]

if __name__ == "__main__":
    k = Kinect()
    k.get_color_frame()
    k.get_depth_frame()

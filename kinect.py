from freenect2 import Device, FrameType

print('Opening Kinect via USB')
device = Device()

def get_color_frame():
    with device.running():
        for type_, frame1 in device:
            if type_ is FrameType.Color:
                break
        return frame1

def get_depth_frame():
    with device.running():
        for type_, frame1 in device:
            if type_ is FrameType.Depth:
                break
        return frame1

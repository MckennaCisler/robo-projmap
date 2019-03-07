from freenect2 import Device, FrameType

device = None

def connect():
    if device is None:
        print('Opening Kinect via USB')
        device = Device()

def get_color_frame():
    connect()
    with device.running():
        for type_, frame1 in device:
            if type_ is FrameType.Color:
                break
    return frame1.to_array().copy()[:, ::-1]

def get_depth_frame():
    connect()
    with device.running():
        for type_, frame1 in device:
            if type_ is FrameType.Depth:
                break
    return frame1.to_array().copy()[:, ::-1]
